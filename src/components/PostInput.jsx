export default function PostInput({
    message,
    setMessage,
    mediaFiles,
    setMediaFiles,
    handlePost
}) {

    const getMediaURL = (file) => {
        if (!file) return null;
        return URL.createObjectURL(file);
    };

    const handleFileChange = (e) => {

        const files = Array.from(e.target.files);

        if (files.length > 6) {
            alert("Maximum 6 files allowed.");
            return;
        }

        setMediaFiles(files);
    };

    return (
        <div className="border border-white/10 rounded-xl p-6 mb-10   hover:bg-white/10 hover:scale-[1.02]
                                transition-all
                                 hover:shadow-[0_0_45px_rgba(0,120,255,0.25)]">

            {/* Textarea */}
            <textarea
                placeholder="Share your space observation..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="w-full bg-transparent outline-none resize-none text-white placeholder-white/50 h-24"
            />

            {/* File Input */}
            <input
                type="file"
                accept="image/*,video/*"
                multiple
                onChange={handleFileChange}
                className="mt-3"
            />

            {/* Preview Grid */}
            {mediaFiles && mediaFiles.length > 0 && (

                <div className="grid grid-cols-3 gap-3 mt-4">

                    {mediaFiles.map((file, index) => {

                        const url = getMediaURL(file);

                        if (file.type.startsWith("image")) {
                            return (
                                <img
                                    key={index}
                                    src={url}
                                    alt="preview"
                                    className="rounded-lg object-cover h-32 w-full"
                                />
                            );
                        }

                        if (file.type.startsWith("video")) {
                            return (
                                <video
                                    key={index}
                                    src={url}
                                    controls
                                    className="rounded-lg h-32 w-full object-cover"
                                />
                            );
                        }

                        return null;
                    })}

                </div>

            )}

            {/* Post Button */}
            <button
                onClick={handlePost}
                className="mt-4 px-6 py-2 bg-blue-500 rounded-lg hover:bg-blue-600 transition"
            >
                Post
            </button>

        </div>
    );
}
