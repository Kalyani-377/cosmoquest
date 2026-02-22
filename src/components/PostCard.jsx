import ReplySection from "./ReplySection";

export default function PostCard({
    post,
    handleLike,
    handleEdit,
    editingId,
    editingText,
    setEditingText,
    saveEdit,
    setEditingId,
    replyingTo,
    setReplyingTo,
    replyText,
    setReplyText,
    handleReply,
    handleDeletePost,
    handleDeleteReply
}) {

    const getMediaURL = (file) => {
        return URL.createObjectURL(file);
    };

    return (
        <div className="border border-white/10 rounded-xl p-6">

            <p className="text-blue-400 font-semibold">
                @{post.author}
            </p>

            <p className="text-xs text-white/40 mb-3">
                {new Date(post.createdAt).toLocaleString()}
            </p>

            {editingId === post.id ? (
                <>
                    <textarea
                        value={editingText}
                        onChange={(e) => setEditingText(e.target.value)}
                        className="w-full bg-black/20 p-2 rounded"
                    />

                    <div className="mt-3 flex gap-4">
                        <button
                            onClick={() => saveEdit(post.id)}
                            className="text-green-400"
                        >
                            Save
                        </button>

                        <button
                            onClick={() => setEditingId(null)}
                            className="text-red-400"
                        >
                            Cancel
                        </button>
                    </div>
                </>
            ) : (
                <>
                    <p className="text-white/80 mb-3">
                        {post.content}
                    </p>

                    {post.media && post.media.length > 0 && (
                        <div className="grid grid-cols-3 gap-3 mb-4">
                            {post.media.map((file, index) => {
                                const url = getMediaURL(file);

                                if (file.type.startsWith("image")) {
                                    return (
                                        <img
                                            key={index}
                                            src={url}
                                            className="rounded-lg object-cover h-40 w-full"
                                        />
                                    );
                                }

                                if (file.type.startsWith("video")) {
                                    return (
                                        <video
                                            key={index}
                                            src={url}
                                            controls
                                            className="rounded-lg h-40 w-full object-cover"
                                        />
                                    );
                                }

                                return null;
                            })}
                        </div>
                    )}
                </>
            )}

            <div className="flex gap-6 text-sm text-white/70">
                <button
                    onClick={() => handleLike(post.id)}
                    className={post.likedByUser ? "text-red-500" : ""}
                >
                    ❤️ {post.likes}
                </button>

                <button onClick={() => handleEdit(post)}>
                    Edit
                </button>

                <button onClick={() => setReplyingTo(post.id)}>
                    Reply
                </button>

                <button
                    onClick={() => handleDeletePost(post.id)}
                    className="hover:text-red-400"
                >
                    Delete
                </button>

            </div>

            <ReplySection
                post={post}
                replyingTo={replyingTo}
                setReplyingTo={setReplyingTo}
                replyText={replyText}
                setReplyText={setReplyText}
                handleReply={handleReply}
                handleDeleteReply={handleDeleteReply}
            />

        </div>
    );
}
