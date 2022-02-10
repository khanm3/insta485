import React from 'react';
import PropTypes from 'prop-types';
import InfiniteScroll from 'react-infinite-scroll-component';
import Post from './post';

class Feed extends React.Component {
  /* Display number of image and post owner of a single post
  */
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      results: [],
      allPosts: [],
      next: '',
    };
    this.fetchMoreData = this.fetchMoreData.bind(this);
    this.appendNewPosts = this.appendNewPosts.bind(this);
    this.getPosts = this.getPosts.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;
    this.getPosts(url);
  }

  getPosts(url) {
    // Call REST API to get the feed information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState(data);
        this.appendNewPosts();
      })
      .catch((error) => console.log(error));
  }

  appendNewPosts() {
    this.setState((prevState) => ({
      allPosts: prevState.allPosts.concat(prevState.results.map((post) => (
        <Post url={post.url} key={post.url} />
      ))),
    }));
  }

  fetchMoreData() {
    const { next } = this.state;
    this.getPosts(next);
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const { next, allPosts } = this.state;

    // Render number of post image and post owner
    return (
      <div className="feed">
        <InfiniteScroll
          dataLength={allPosts.length}
          next={this.fetchMoreData}
          hasMore={() => next !== ''}
        >
          {allPosts}
        </InfiniteScroll>
      </div>
    );
  }
}

Feed.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Feed;
