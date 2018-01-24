import { combineReducers } from 'redux'

import {
  SET_FILTER,
  REQUEST_THREADS,
  RECEIVE_THREADS,
  RESTART_SERVER,
  SERVER_RESTARTED
} from './actions'

function filterStr(state = 'tag:flagged', action) {
  switch (action.type) {
    case SET_FILTER:
      return action.filterStr
    default:
      return state
  }
}

function server(state = {}, action) {
    switch (action.type) {
        case RESTART_SERVER:
            return Object.assign({}, state, {
                isLoading: true
            })
        case SERVER_RESTARTED:
            return Object.assign({}, state, {
                isLoading: false
            })
        default:
            return state
    }
}

function threads(state = {isLoading: false, items: [] }, action) {
  switch (action.type) {
    case REQUEST_THREADS:
      return Object.assign({}, state, {
        isLoading: true
      })
    case RECEIVE_THREADS:
      return Object.assign({}, state, {
        isLoading: false,
        items: action.threads,
        lastUpdated: action.receivedAt
      })
    default:
      return state
  }
}

function filterThreads(state = {}, action) {
  switch (action.type) {
    case RECEIVE_THREADS:
    case REQUEST_THREADS:
      return Object.assign({}, state, {
        [action.filterStr]: threads(state[action.filterStr], action)
      })
    default:
      return state
  }
}

const rootReducer = combineReducers({
    filterThreads,
    filterStr,
    server
})

export default rootReducer
