import { useState } from "react";
import TopNavbar from "../components/topnav";
import PostInput from "../components/PostInput";
import PostCard from "../components/PostCard";

export default function Talk() {

    const [message, setMessage] = useState("");
    const [mediaFiles, setMediaFiles] = useState([]);

    const [editingId, setEditingId] = useState(null);
    const [editingText, setEditingText] = useState("");

    const [replyingTo, setReplyingTo] = useState(null);
    const [replyText, setReplyText] = useState("");

    const [posts, setPosts] = useState([]);

    // CREATE POST
    const handlePost = () => {

        if (!message.trim() && mediaFiles.length === 0) return;

        const newPost = {
            id: Date.now(),
            author: "You",
            content: message,
            likes: 0,
            media: mediaFiles,
            replies: [],
            createdAt: new Date()
        };

        setPosts(prev => [newPost, ...prev]);
        setMessage("");
        setMediaFiles([]);
    };

    // LIKE
    const handleLike = (id) => {

        setPosts(prev =>
            prev.map(post => {

                if (post.id !== id) return post;

                // If already liked → unlike
                if (post.likedByUser) {
                    return {
                        ...post,
                        likes: post.likes - 1,
                        likedByUser: false
                    };
                }

                // If not liked → like
                return {
                    ...post,
                    likes: post.likes + 1,
                    likedByUser: true
                };
            })
        );
    };


    // EDIT
    const handleEdit = (post) => {
        setEditingId(post.id);
        setEditingText(post.content);
    };

    const saveEdit = (id) => {
        setPosts(prev =>
            prev.map(post =>
                post.id === id
                    ? { ...post, content: editingText }
                    : post
            )
        );
        setEditingId(null);
        setEditingText("");
    };

    // DELETE POST
    const handleDeletePost = (id) => {
        setPosts(prev => prev.filter(post => post.id !== id));
    };

    // REPLY
    const handleReply = (id) => {

        if (!replyText.trim()) return;

        setPosts(prev =>
            prev.map(post =>
                post.id === id
                    ? {
                        ...post,
                        replies: [
                            ...post.replies,
                            {
                                id: Date.now(),
                                author: "You",
                                content: replyText
                            }
                        ]
                    }
                    : post
            )
        );

        setReplyingTo(null);
        setReplyText("");
    };

    // DELETE REPLY
    const handleDeleteReply = (postId, replyId) => {
        setPosts(prev =>
            prev.map(post =>
                post.id === postId
                    ? {
                        ...post,
                        replies: post.replies.filter(r => r.id !== replyId)
                    }
                    : post
            )
        );
    };

    return (
        <div className=" min-h-screen text-white">

            <TopNavbar />

            <div className="max-w-4xl mx-auto px-6 py-16">

                <h1 className="text-4xl font-bold mb-10">
                    Community Talk
                </h1>

                <PostInput
                    message={message}
                    setMessage={setMessage}
                    mediaFiles={mediaFiles}
                    setMediaFiles={setMediaFiles}
                    handlePost={handlePost}
                />

                {posts.length === 0 ? (
                    <div className="text-center text-white/40 mt-20 ">
                        No posts yet. Be the first to share something 🚀
                    </div>
                ) : (
                    <div className="space-y-6">
                        {posts.map(post => (
                            <PostCard
                                key={post.id}
                                post={post}
                                handleLike={handleLike}
                                handleEdit={handleEdit}
                                editingId={editingId}
                                editingText={editingText}
                                setEditingText={setEditingText}
                                saveEdit={saveEdit}
                                setEditingId={setEditingId}
                                replyingTo={replyingTo}
                                setReplyingTo={setReplyingTo}
                                replyText={replyText}
                                setReplyText={setReplyText}
                                handleReply={handleReply}
                                handleDeletePost={handleDeletePost}
                                handleDeleteReply={handleDeleteReply}
                            />
                        ))}
                    </div>
                )}

            </div>
        </div>
    );
}
