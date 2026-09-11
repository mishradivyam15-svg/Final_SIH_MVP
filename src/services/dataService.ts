/**
 * Single switch point between mock data and the real FastAPI backend.
 *
 * Every page/hook imports from HERE, never directly from `api.ts` or
 * `mockApi.ts`. This is what lets `VITE_USE_MOCK_DATA` flip the entire
 * app's data source without touching any UI code.
 *
 * HYBRID MODE: `submitReport` always calls the real backend regardless
 * of the mock flag, because it is the only endpoint currently
 * implemented in the backend. Browse features (dashboard, precursors,
 * reports) use mock data until those backend endpoints exist.
 */

import * as realApi from './api';
import * as mockApi from './mockApi';

const USE_MOCK = (import.meta.env.VITE_USE_MOCK_DATA as string | undefined) !== 'false';

const impl = USE_MOCK ? mockApi : realApi;

export const getDashboard = impl.getDashboard;
export const getPrecursors = impl.getPrecursors;
export const getPrecursor = impl.getPrecursor;
export const getRelationships = impl.getRelationships;
export const getReport = impl.getReport;
export const getReportsByIds = impl.getReportsByIds;
export const submitReview = impl.submitReview;

// submitReport always calls the real backend — it is the primary
// integration point and the endpoint exists on the FastAPI server.
export const submitReport = realApi.submitReport;

export const isMockMode = USE_MOCK;

export { ApiError } from './api';

