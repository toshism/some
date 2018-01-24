import React, { Component } from 'react'
import PropTypes from 'prop-types'
import moment from 'moment';

export default class Threads extends Component {
    handleClick = (e) => {
        console.log(e.target);
    }

    render() {
        return (
            <table>
            <tbody>
                {this.props.threads.map((thread, i) => {
                    let formattedDate = moment(thread.date);
                    return (
                        <tr onClick={this.handleClick} key={thread.thread_id}>
                        <td>{formattedDate.fromNow()}</td>
                        <td>{thread.subject.substring(0, 50)}</td>
                        <td>{thread.authors}</td>
                        <td>{thread.tags.join('|')}</td>
                        </tr>
                    )
                })}
            </tbody>
            </table>
        )
    }
}

Threads.propTypes = {
    threads: PropTypes.array.isRequired
}
