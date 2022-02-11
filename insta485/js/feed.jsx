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
      allNoRender: [],
    };
    this.fetchMoreData = this.fetchMoreData.bind(this);
    this.appendNewPosts = this.appendNewPosts.bind(this);
    this.getPosts = this.getPosts.bind(this);
  }

  componentDidMount() {
    console.log(new Date());
    console.log(window.performance.getEntriesByType('navigation')[0].type);
    if (window.performance.getEntriesByType('navigation')[0].type === 'back_forward') {
      const data = JSON.parse(window.history.state);
      /* data.allPosts.forEach((value, index) => {
        const temp = value;
        temp.$$typeof = Symbol(react.element);
        data.allPosts[index] = temp;
      }); */
      console.log(data);
      this.setState(data);
    } else {
      // This line automatically assigns this.props.url to the const variable url
      const { url } = this.props;
      this.getPosts(url);
    }
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
        /* const { results, allPosts, next } = this.state;
        const hist = { results, allPosts, next, };
        console.log(this.state); */
        const { results, next, allNoRender } = this.state;
        const hist = { results, next, allNoRender };
        window.history.replaceState(JSON.stringify(hist), 'Index', '/');
      })
      .catch((error) => console.log(error));
  }

  appendNewPosts() {
    this.setState((prevState) => ({
      allPosts: prevState.allPosts.concat(prevState.results.map((post) => (
        <Post url={post.url} key={post.url} />
      ))),
      allNoRender: prevState.allNoRender.concat(prevState.results),
    }));
  }

  fetchMoreData() {
    const { next } = this.state;
    this.getPosts(next);
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const { next, allPosts, allNoRender } = this.state;

    // Render number of post image and post owner
    console.log("render");
    console.log(this.state);
    let render = allPosts;
    if (allPosts.length === 0) {
      render = allNoRender.map((post) => (<Post url={post.url} key={post.url} />));
    }
    return (
      <div className="feed">
        <InfiniteScroll
          dataLength={allPosts.length}
          next={this.fetchMoreData}
          hasMore={() => next !== ''}
        >
          {render}
        </InfiniteScroll>
      </div>
    );
  }
}

Feed.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Feed;
