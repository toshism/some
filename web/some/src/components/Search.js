import React, { Component } from 'react'
import PropTypes from 'prop-types'
import debounce from 'debounce'

export default class Search extends Component {

    constructor(props) {
        super(props);
        this.handleChange = debounce(this.handleChange, 300);
        this.state = {searchStr: this.props.value}
    }

    handleChange = (filterStr) => {
        this.setState({searchStr: filterStr})
        this.props.onChange(filterStr)
    }

    handleSubmit = (event) => {
        event.preventDefault();
        this.props.onChange(this.state.searchStr);
    }

    handleClick = (event) => {
        event.preventDefault();
        this.props.onChange()
    }

    render() {
        const { value, options } = this.props

        return (
            <form onSubmit={this.handleSubmit}>
                <input type="text" defaultValue={value} onChange={e => this.handleChange(e.target.value)} />
                <button type="submit">search</button>
            </form>
        )
    }
}

Search.propTypes = {
    options: PropTypes.arrayOf(PropTypes.string.isRequired).isRequired,
    value: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired
}
