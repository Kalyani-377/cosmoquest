export default function ReplySection({
    post,
    replyingTo,
    setReplyingTo,
    replyText,
    setReplyText,
    handleReply,
    handleDeleteReply
}) {

    return (
        <>
            {replyingTo === post.id && (
                <div className="mt-3">
                    <input
                        value={replyText}
                        onChange={(e) => setReplyText(e.target.value)}
                        placeholder="Write reply..."
                        className="bg-black/20 p-2 rounded w-full"
                    />
                    <button
                        onClick={() => handleReply(post.id)}
                        className="text-blue-400 mt-2"
                    >
                        Send Reply
                    </button>
                </div>
            )}

            {post.replies.length > 0 && (
                <div className="mt-4 pl-4 border-l border-white/20 space-y-3">
                    {post.replies.map(reply => (
                        <div key={reply.id} className="flex justify-between">

                            <div>
                                <p className="text-blue-300 text-sm">
                                    @{reply.author}
                                </p>
                                <p className="text-white/70 text-sm">
                                    {reply.content}
                                </p>
                            </div>

                            <button
                                onClick={() =>
                                    handleDeleteReply(post.id, reply.id)
                                }
                                className="text-xs text-red-400"
                            >
                                Delete
                            </button>

                        </div>
                    ))}
                </div>
            )}
        </>
    );
}
