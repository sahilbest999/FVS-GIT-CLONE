/* eslint-disable import/no-named-as-default */
import { applyMiddleware, configureStore } from '@reduxjs/toolkit';

import AppSettingsReducer from './AppSettingsSlicer';
import User_Repository_Reducer, {
  USER_REPOSITORY_DATA_STRUCTURE,
  addRepository,
} from './UserRepositorySlicer';
import SynchronizationSlice, {
  SYNC_DATA_STRUCTURE,
  SYNC_ACTIONS,
  allocateRepoData,
  updateUploadingQueue,
  addUploadFinishedQueue,
  ReAddFailedUpload,
} from './SynchronizationSlicer';
import { LOAD_UPLOADS_FROM_REPOSITORY, updateSync } from '../backgroundTasks';

export default configureStore({
  reducer: {
    AppSettings: AppSettingsReducer,
    UserRepoData: User_Repository_Reducer,
    Sync: SynchronizationSlice,
  },
  enhancers: [
    applyMiddleware((storeAPI) => (next) => (action) => {
      // eslint-disable-next-line default-case
      (async () => {
        switch (action.type) {
          case addRepository.type:
            next(action);
            LOAD_UPLOADS_FROM_REPOSITORY();
            break;
          case allocateRepoData.type:
            next(action);
            updateSync();
            break;
          case addUploadFinishedQueue.type:
            next(action);
            updateSync();
            break;
          case ReAddFailedUpload.type:
            next(action);
            updateSync();
            break;
          default:
            next(action);
        }
      })();
    }),
  ],
});

// eslint-disable-next-line @typescript-eslint/naming-convention
export interface store {
  AppSettings: any;
  UserRepoData: USER_REPOSITORY_DATA_STRUCTURE;
  Sync: SYNC_DATA_STRUCTURE;
}
