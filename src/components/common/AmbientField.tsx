import { useEffect, useRef } from 'react';
import {
  BufferAttribute,
  BufferGeometry,
  Color,
  Group,
  LineBasicMaterial,
  LineSegments,
  PerspectiveCamera,
  Points,
  PointsMaterial,
  Scene,
  WebGLRenderer,
} from 'three';

const PARTICLE_COUNT = 70;
const LINK_DISTANCE = 190;
const FIELD = { x: 1700, y: 950, z: 700 };

/**
 * Ambient WebGL backdrop: a drifting particle constellation whose nearby
 * points link up and fall apart again. It deliberately mirrors what the
 * product does — discrete reports that turn out to be connected — rather
 * than being generic decoration.
 *
 * Sits behind all content, never takes pointer events, pauses when the tab
 * is hidden, and renders a single static frame under reduced-motion.
 */
export function AmbientField() {
  const mountRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    let renderer: WebGLRenderer;
    try {
      renderer = new WebGLRenderer({
        alpha: true,
        antialias: false,
        powerPreference: 'low-power',
      });
    } catch {
      return; // No WebGL — the page simply renders without the backdrop.
    }

    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    renderer.setClearColor(0x000000, 0);
    mount.appendChild(renderer.domElement);

    const scene = new Scene();
    const camera = new PerspectiveCamera(60, mount.clientWidth / mount.clientHeight, 1, 4000);
    camera.position.z = 1000;

    const group = new Group();
    scene.add(group);

    // ── Particles ────────────────────────────────────────────────
    const positions = new Float32Array(PARTICLE_COUNT * 3);
    const velocities = new Float32Array(PARTICLE_COUNT * 3);

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      positions[i * 3] = (Math.random() - 0.5) * FIELD.x;
      positions[i * 3 + 1] = (Math.random() - 0.5) * FIELD.y;
      positions[i * 3 + 2] = (Math.random() - 0.5) * FIELD.z;
      velocities[i * 3] = (Math.random() - 0.5) * 0.45;
      velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.45;
      velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.3;
    }

    const pointGeometry = new BufferGeometry();
    pointGeometry.setAttribute('position', new BufferAttribute(positions, 3));

    const pointMaterial = new PointsMaterial({
      color: new Color('#7aa8d9'),
      size: 4.5,
      sizeAttenuation: true,
      transparent: true,
      opacity: 0.85,
      depthWrite: false,
    });
    group.add(new Points(pointGeometry, pointMaterial));

    // ── Links ────────────────────────────────────────────────────
    // Preallocated to the theoretical maximum so no buffers are created
    // per frame; setDrawRange controls how much is actually drawn.
    const maxSegments = (PARTICLE_COUNT * (PARTICLE_COUNT - 1)) / 2;
    const linkPositions = new Float32Array(maxSegments * 6);
    const linkColors = new Float32Array(maxSegments * 6);

    const linkGeometry = new BufferGeometry();
    const linkPositionAttr = new BufferAttribute(linkPositions, 3);
    const linkColorAttr = new BufferAttribute(linkColors, 3);
    linkPositionAttr.setUsage(35048 /* DynamicDrawUsage */);
    linkColorAttr.setUsage(35048);
    linkGeometry.setAttribute('position', linkPositionAttr);
    linkGeometry.setAttribute('color', linkColorAttr);

    const linkMaterial = new LineBasicMaterial({
      vertexColors: true,
      transparent: true,
      opacity: 0.55,
      depthWrite: false,
    });
    group.add(new LineSegments(linkGeometry, linkMaterial));

    const updateLinks = () => {
      let vertexPairs = 0;

      for (let i = 0; i < PARTICLE_COUNT; i++) {
        for (let j = i + 1; j < PARTICLE_COUNT; j++) {
          const dx = positions[i * 3] - positions[j * 3];
          const dy = positions[i * 3 + 1] - positions[j * 3 + 1];
          const dz = positions[i * 3 + 2] - positions[j * 3 + 2];
          const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
          if (distance > LINK_DISTANCE) continue;

          // Fade toward the page background as the link stretches. On a
          // near-black ground, dimming RGB reads as fading out — which
          // LineBasicMaterial can do per-vertex, unlike alpha.
          const strength = 1 - distance / LINK_DISTANCE;
          const o = vertexPairs * 6;

          linkPositions[o] = positions[i * 3];
          linkPositions[o + 1] = positions[i * 3 + 1];
          linkPositions[o + 2] = positions[i * 3 + 2];
          linkPositions[o + 3] = positions[j * 3];
          linkPositions[o + 4] = positions[j * 3 + 1];
          linkPositions[o + 5] = positions[j * 3 + 2];

          const r = 0.36 * strength;
          const g = 0.55 * strength;
          const b = 0.78 * strength;
          linkColors[o] = r;
          linkColors[o + 1] = g;
          linkColors[o + 2] = b;
          linkColors[o + 3] = r;
          linkColors[o + 4] = g;
          linkColors[o + 5] = b;

          vertexPairs++;
        }
      }

      linkGeometry.setDrawRange(0, vertexPairs * 2);
      linkPositionAttr.needsUpdate = true;
      linkColorAttr.needsUpdate = true;
    };

    // ── Interaction + loop ───────────────────────────────────────
    const pointer = { x: 0, y: 0 };
    const onPointerMove = (event: MouseEvent) => {
      pointer.x = (event.clientX / window.innerWidth) * 2 - 1;
      pointer.y = (event.clientY / window.innerHeight) * 2 - 1;
    };

    const onResize = () => {
      if (!mount.clientWidth || !mount.clientHeight) return;
      camera.aspect = mount.clientWidth / mount.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(mount.clientWidth, mount.clientHeight);
    };

    let frame = 0;
    const animate = () => {
      frame = requestAnimationFrame(animate);
      if (document.hidden) return;

      for (let i = 0; i < PARTICLE_COUNT; i++) {
        for (let axis = 0; axis < 3; axis++) {
          const k = i * 3 + axis;
          positions[k] += velocities[k];
          const bound = axis === 0 ? FIELD.x / 2 : axis === 1 ? FIELD.y / 2 : FIELD.z / 2;
          if (positions[k] > bound || positions[k] < -bound) velocities[k] *= -1;
        }
      }
      pointGeometry.attributes.position.needsUpdate = true;
      updateLinks();

      // Gentle parallax toward the cursor, easing rather than snapping.
      group.rotation.y += (pointer.x * 0.16 - group.rotation.y) * 0.02;
      group.rotation.x += (pointer.y * 0.1 - group.rotation.x) * 0.02;

      renderer.render(scene, camera);
    };

    updateLinks();

    if (prefersReduced) {
      renderer.render(scene, camera);
    } else {
      window.addEventListener('mousemove', onPointerMove, { passive: true });
      animate();
    }
    window.addEventListener('resize', onResize);

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('mousemove', onPointerMove);
      window.removeEventListener('resize', onResize);
      pointGeometry.dispose();
      pointMaterial.dispose();
      linkGeometry.dispose();
      linkMaterial.dispose();
      renderer.dispose();
      if (renderer.domElement.parentNode === mount) {
        mount.removeChild(renderer.domElement);
      }
    };
  }, []);

  return <div ref={mountRef} className="ambient-field" aria-hidden="true" />;
}
