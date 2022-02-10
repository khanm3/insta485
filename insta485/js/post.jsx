import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';

class Post extends React.Component {
  /* Display number of image and post owner of a single post
   */
  constructor(props) {
    // Initialize mutable state
    super(props);
    this.state = {
      imgUrl: '',
      owner: '',
      ownerImgUrl: '',
      ownerShowUrl: '',
      postShowUrl: '',
      postid: '',
      created: '',
      likes: {},
      comments: [],
      commentFormText: '',
    };
    this.handleChange = this.handleChange.bind(this);
    this.handleCommentCreate = this.handleCommentCreate.bind(this);
    this.handleCommentDelete = this.handleCommentDelete.bind(this);
    this.handleLike = this.handleLike.bind(this);
  }

  componentDidMount() {
    // This line automatically assigns this.props.url to the const variable url
    const { url } = this.props;

    // Call REST API to get the post's information
    fetch(url, { credentials: 'same-origin' })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState(data);
        // this.setState({
        //   imgUrl: data.imgUrl,
        //   owner: data.owner,
        // });
      })
      .catch((error) => console.log(error));
  }

  handleChange(event) {
    this.setState({ commentFormText: event.target.value });
  }

  handleLike() {
    const { postid, likes } = this.state;
    if (likes.lognameLikesThis) {
      console.log('here');
      fetch(likes.url, {
        method: 'DELETE',
        credentials: 'same-origin',
      })
        .then(() => {
          const tempLikes = {
            lognameLikesThis: false,
            numLikes: likes.numLikes - 1,
            url: null,
          };

          this.setState({ likes: tempLikes });
        })
        .catch((error) => console.log(error));
    } else {
      console.log('why');
      const url = `/api/v1/likes/?postid=${postid}`;
      fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          Accept: 'application/json',
        },
      })
        .then((response) => {
          if (!response.ok) throw Error(response.statusText);
          return response.json();
        })
        .then((data) => {
          const tempLikes = {
            lognameLikesThis: true,
            numLikes: likes.numLikes + 1,
            url: data.url,
          };
          this.setState({ likes: tempLikes });
        })
        .catch((error) => console.log(error));
    }
  }

  handleCommentCreate(event) {
    const { commentFormText, postid } = this.state;
    const bodyData = { text: commentFormText };

    const url = `/api/v1/comments/?postid=${postid}`;
    fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(bodyData),
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        return response.json();
      })
      .then((data) => {
        this.setState((prevState) => ({
          comments: prevState.comments.concat([data]),
        }));
      })
      .catch((error) => console.log(error));

    console.log(commentFormText);
    this.setState({ commentFormText: '' });
    event.target.reset();
    event.preventDefault();
  }

  handleCommentDelete(commentid) {
    const url = `/api/v1/comments/${commentid}/`;
    fetch(url, {
      method: 'DELETE',
      credentials: 'same-origin',
    })
      .then((response) => {
        if (!response.ok) throw Error(response.statusText);
        this.setState((prevState) => ({
          comments: prevState.comments.filter((comment) => comment.commentid !== commentid),
        }));
      })
      .catch((error) => console.log(error));
  }

  render() {
    // This line automatically assigns this.state.imgUrl to the const variable imgUrl
    // and this.state.owner to the const variable owner
    const {
      imgUrl, owner, ownerShowUrl, ownerImgUrl, postShowUrl, created, likes, comments,
    } = this.state;
    const createdHumanized = moment.utc(created, 'YYYY-MM-DD HH:mm:ss').fromNow();
    // Render number of post image and post owner
    return (
      <div className="post">
        <div className="header">
          <a href={ownerShowUrl}>
            <img className="user_img" alt="user" src={ownerImgUrl} />
          </a>
          <a href={ownerShowUrl}><h3>{owner}</h3></a>
          <a href={postShowUrl} className="push_right color_grey"><h3>{createdHumanized}</h3></a>
        </div>
        <img className="post_img" onDoubleClick={() => { if (!likes.lognameLikesThis) { this.handleLike(); } }} src={imgUrl} alt="post" />
        <p>
          {likes.numLikes}
          {likes.numLikes === 1 ? ' like' : ' likes'}
        </p>
        <button type="button" className="like-unlike-button" onClick={() => this.handleLike()}>
          {likes.lognameLikesThis ? 'unlike' : 'like'}
        </button>
        {comments.map((comment) => (
          <p key={comment.commentid}>
            <b><a href={comment.ownerShowUrl}>{comment.owner}</a></b>
            {' '}
            {comment.text}
            {comment.lognameOwnsThis && (
              <button type="button" className="delete-comment-button" onClick={() => this.handleCommentDelete(comment.commentid)}>
                Delete comment
              </button>
            )}
          </p>
        ))}
        <form className="comment-form" onSubmit={this.handleCommentCreate}>
          <input type="text" defaultValue="" onChange={this.handleChange} />
        </form>
      </div>
    );
  }
}

Post.propTypes = {
  url: PropTypes.string.isRequired,
};

export default Post;
