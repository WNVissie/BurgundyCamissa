import React, { useState, useEffect } from 'react';
import { communityAPI } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Textarea } from '../components/ui/textarea';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { format } from 'date-fns';
import { MessageCircle, Plus, Send } from 'lucide-react';

export function Community() {
  const { user, isAdmin, isManager } = useAuth();
  const [posts, setPosts] = useState([]);
  const [selectedPost, setSelectedPost] = useState(null);
  const [newPost, setNewPost] = useState({ title: '', content: '', post_type: 'Question' });
  const [newReply, setNewReply] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const res = await communityAPI.getPosts();
      setPosts(res.data);
    } catch (err) {
      setError('Failed to load community posts.');
    } finally {
      setLoading(false);
    }
  };

  const fetchPostDetails = async (postId) => {
    try {
      setLoading(true);
      const res = await communityAPI.getPost(postId);
      setSelectedPost(res.data);
    } catch (err) {
      setError('Failed to load post details.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePost = async (e) => {
    e.preventDefault();
    try {
      await communityAPI.createPost(newPost);
      setNewPost({ title: '', content: '', post_type: 'Question' });
      fetchPosts();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create post.');
    }
  };

  const handleAddReply = async (e) => {
    e.preventDefault();
    if (!newReply.trim()) return;
    try {
      await communityAPI.addReply(selectedPost.id, { content: newReply });
      setNewReply('');
      fetchPostDetails(selectedPost.id); // Refresh post details to show new reply
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add reply.');
    }
  };

  if (loading && !selectedPost) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  if (selectedPost) {
    return (
      <div>
        <Button onClick={() => setSelectedPost(null)} className="mb-4">
          &larr; Back to All Posts
        </Button>
        <Card>
          <CardHeader>
            <CardTitle>{selectedPost.title}</CardTitle>
            <CardDescription>
              Posted by {selectedPost.author.name} on {format(new Date(selectedPost.created_at), 'PPP')}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap">{selectedPost.content}</p>
            <hr className="my-6" />
            <h3 className="font-semibold mb-4">Replies ({selectedPost.reply_count})</h3>
            <div className="space-y-4">
              {selectedPost.replies.map(reply => (
                <div key={reply.id} className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm">{reply.content}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    - {reply.author.name} on {format(new Date(reply.created_at), 'Pp')}
                  </p>
                </div>
              ))}
            </div>
            <form onSubmit={handleAddReply} className="mt-6 flex space-x-2">
              <Textarea
                value={newReply}
                onChange={(e) => setNewReply(e.target.value)}
                placeholder="Write a reply..."
                required
              />
              <Button type="submit"><Send className="h-4 w-4" /></Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <MessageCircle className="h-5 w-5 mr-2" />
            Community Board
          </CardTitle>
          <CardDescription>Ask questions, share information, and view announcements.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreatePost} className="space-y-4 p-4 border rounded-lg">
            <h3 className="font-semibold">Create a New Post</h3>
            <Input
              placeholder="Title"
              value={newPost.title}
              onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
              required
            />
            <Textarea
              placeholder="What's on your mind?"
              value={newPost.content}
              onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
              required
            />
            {(isAdmin() || isManager()) && (
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="is-announcement"
                  checked={newPost.post_type === 'Announcement'}
                  onChange={(e) => setNewPost({ ...newPost, post_type: e.target.checked ? 'Announcement' : 'Question' })}
                />
                <label htmlFor="is-announcement" className="text-sm">Post as Announcement</label>
              </div>
            )}
            <Button type="submit"><Plus className="h-4 w-4 mr-2" />Post</Button>
          </form>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {posts.map(post => (
          <Card key={post.id} className="cursor-pointer hover:bg-gray-50" onClick={() => fetchPostDetails(post.id)}>
            <CardContent className="p-4 flex justify-between items-center">
              <div>
                <div className="flex items-center space-x-2">
                  {post.post_type === 'Announcement' && <Badge>Announcement</Badge>}
                  <h3 className="font-semibold">{post.title}</h3>
                </div>
                <p className="text-sm text-gray-500">
                  by {post.author.name} on {format(new Date(post.created_at), 'PPP')}
                </p>
              </div>
              <div className="text-sm text-gray-500">{post.reply_count} replies</div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
