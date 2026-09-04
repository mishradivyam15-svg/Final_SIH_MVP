/**
 * Single switch point between mock data and the real FastAPI backend.
 *
 * Every page/hook imports from HERE, never directly from `api.ts` or
 * `mockApi.ts`. This is what lets `VITE_USE_MOCK_DATA` flip the entire
 * app's data source without touching any UI code (see requirement #66
 * in the project brief: no `if (mock) {...} else {...}` scattered in
 * components).
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

export const isMockMode = USE_MOCK;

export { ApiError } from './api';
