/**
 * Shared utility functions for Pickr frontend
 */

/**
 * Formats a size in MB, converting to GB or KB if appropriate.
 * @param {number} megabytes 
 * @returns {string}
 */
export const formatSize = (megabytes) => {
    if (megabytes >= 1024) {
        return `${(megabytes / 1024).toFixed(1)} GB`;
    }
    if (megabytes < 1) {
        return `${(megabytes * 1024).toFixed(0)} KB`;
    }
    return `${megabytes.toFixed(0)} MB`;
};

/**
 * Estimates space saved based on photo count.
 * (Simple MVP estimation: 3MB per photo)
 * @param {number} count 
 * @returns {string}
 */
export const estimateSpaceSaved = (count) => {
    return formatSize(count * 3);
};

/**
 * Formats a date string for display.
 * @param {string|Date} date 
 * @returns {string}
 */
export const formatDate = (date) => {
    const d = new Date(date);
    return d.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
};
/**
 * Returns a readable quality label based on a 0-1 score.
 * @param {number} score 
 * @returns {string}
 */
export const getQualityLabel = (score) => {
    if (score > 0.8) return 'High Quality';
    if (score > 0.5) return 'Med Quality';
    return 'Low Quality';
};

/**
 * Resizes an image file to a maximum dimension while maintaining aspect ratio.
 * @param {File} file 
 * @param {number} maxDimension 
 * @returns {Promise<Blob>}
 */
export const resizeImage = (file, maxDimension = 1600) => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                let width = img.width;
                let height = img.height;

                if (width > height) {
                    if (width > maxDimension) {
                        height *= maxDimension / width;
                        width = maxDimension;
                    }
                } else {
                    if (height > maxDimension) {
                        width *= maxDimension / height;
                        height = maxDimension;
                    }
                }

                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);

                canvas.toBlob((blob) => {
                    resolve(blob);
                }, file.type, 0.85); // 85% quality JPEG/PNG
            };
            img.onerror = reject;
            img.src = e.target.result;
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
};
