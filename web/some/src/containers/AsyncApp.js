import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import {
    setFilter,
    fetchThreads,
    fetchRestartServer
} from '../actions'
import Search from '../components/Search'
import Threads from '../components/Threads'

class AsyncApp extends Component {
  constructor(props) {
    super(props)
    this.handleChange = this.handleChange.bind(this)
    this.handleRefreshClick = this.handleRefreshClick.bind(this)
    this.handleRestart = this.handleRestart.bind(this)
  }

  componentDidMount() {
    const { dispatch, filterStr } = this.props
    dispatch(fetchThreads(filterStr))
  }

  componentDidUpdate(prevProps) {
    if (this.props.filterStr !== prevProps.filterStr) {
      const { dispatch, filterStr } = this.props
      dispatch(fetchThreads(filterStr))
    }
  }

  handleChange(nextFilterStr) {
    this.props.dispatch(setFilter(nextFilterStr))
    this.props.dispatch(fetchThreads(nextFilterStr))
  }

  handleRefreshClick(e) {
    e.preventDefault()

    const { dispatch, filterStr } = this.props
    dispatch(fetchThreads(filterStr))
  }

  handleRestart(e) {
      e.preventDefault()
      const { dispatch } = this.props
      dispatch(fetchRestartServer())
  }

  render() {
    const { filterStr, threads, isLoading, lastUpdated } = this.props
    return (
      <div>
        <Search
          value={filterStr}
          onChange={this.handleChange}
          options={['tag:new', 'tag:unread', 'tag:flagged']}
        />
        <p><button onClick={this.handleRestart}>Restart Server</button></p>
        <p>
          {lastUpdated &&
            <span>
              Last updated at {new Date(lastUpdated).toLocaleTimeString()}.
              {' '}
            </span>}
          {!isLoading &&
            <button onClick={this.handleRefreshClick}>
              Refresh
            </button>}
        </p>
        {isLoading && threads.length === 0 && <h2>Loading...</h2>}
        {!isLoading && threads.length === 0 && <h2>Empty.</h2>}
        {threads.length > 0 &&
          <div style={{ opacity: isLoading ? 0.5 : 1 }}>
            <Threads threads={threads} />
          </div>}
      </div>
    )
  }
}

AsyncApp.propTypes = {
  filterStr: PropTypes.string.isRequired,
  threads: PropTypes.array.isRequired,
  isLoading: PropTypes.bool.isRequired,
  lastUpdated: PropTypes.number,
  dispatch: PropTypes.func.isRequired
}

function mapStateToProps(state) {
  const { filterStr, filterThreads } = state
  const {
    isLoading,
    lastUpdated,
    items: threads
  } = filterThreads[filterStr] || {
    isLoading: true,
    items: []
  }

  return {
    filterStr,
    threads,
    isLoading,
    lastUpdated
  }
}

export default connect(mapStateToProps)(AsyncApp)
