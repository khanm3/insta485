import React from 'react';
import PropTypes from 'prop-types';
import Post from './post';

class Feed extends React.Component {
  /* Display number of image and post owner of a single post
  */
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      results: [],
      next: '',
    };
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;
    // Call REST API to get the feed information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState(data);
      })
      .catch((error) => console.log(error));
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const { results } = this.state;
    // Render number of post image and post owner
    return (
      <div className="feed">
        {results.map((post) => (
          <Post url={post.url} />
        ))}
      </div>
    );
  }
}

Feed.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Feed;
