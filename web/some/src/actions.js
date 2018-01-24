export const SET_FILTER = 'SET_FILTER';
export const REQUEST_THREADS = 'REQUEST_THREADS';
export const RECEIVE_THREADS = 'RECEIVE_THREADS';
export const RESTART_SERVER = 'RESTART_SERVER';
export const SERVER_RESTARTED = 'SERVER_RESTARTED';

export const setFilter = (filterStr) => {
    return {
        type: 'SET_FILTER',
        filterStr
    }
};

export const requestThreads = (filterStr) => {
    return {
        type: 'REQUEST_THREADS',
        filterStr
    }
};

function receiveThreads(filterStr, json) {
    return {
        type: RECEIVE_THREADS,
        filterStr,
        threads: json.threads.map(child => child),
        receivedAt: Date.now()
    }
};

function restartServer() {
    return {
        type: RESTART_SERVER
    }
};

function serverRestarted(){
    return {
        type: SERVER_RESTARTED
    }
}

export function fetchRestartServer() {
    return function(dispatch) {
        dispatch(restartServer())
        return fetch('http://localhost:8080/api/server/restart')
            .then(response => {},
                  error => dispatch(serverRestarted)
            )
    }
};

export function fetchThreads(filterStr) {
  return function (dispatch) {
    dispatch(requestThreads(filterStr))
    return fetch(`http://localhost:8080/api/threads/${filterStr}`)
      .then(
          response => {
              return response.json()
          },
        error => console.log('An error occurred.', error)
      )
      .then(json =>
        dispatch(receiveThreads(filterStr, json))
      )
  }
}
