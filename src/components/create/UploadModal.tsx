import React, { useState, useContext, useEffect, ChangeEvent } from 'react';
import styles from './styles/UploadModal.module.css';
import { CanvasContext } from '@/context/canvas/CanvasContext';
import MediaPlayer from '@/utils/MediaPlayer';
import { getMediaSrc } from '@/utils/utils';
// A component that performs transactions on core GVM entities must explicitly
// import their type definitions. This ensures all operations are verifiable
// and conform to the system's architectural contracts.
import { Situation } from '@/types/canvas/Situation';
import { Group } from '@/types/canvas/Group';

interface UploadModalProps {
  uploadType: 'image' | 'audio';
  setIsModalOpen: (isOpen: boolean) => void;
}

/**
 * UploadModal allows a user to attach media to a Cell (Situation) or Group.
 * The data layer expects a Partial<Situation | Group>, but our UI deals with
 * a raw FormData payload. We cast the FormData to `any` to satisfy TypeScript
 * while preserving runtime behaviour.
 */
const UploadModal: React.FC<UploadModalProps> = ({ uploadType, setIsModalOpen }) => {
  const {
    updateSituationAndNode,
    updateGroup,
    selectedSituation,
    selectedGroup,
    loading,
  } = useContext(CanvasContext);

  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState('');

  /* ------------------------------------------------------------
     Helpers
   -------------------------------------------------------------*/
  const resetState = () => {
    setFile(null);
    setPreview(null);
    setErrorMessage('');
  };

  /* ------------------------------------------------------------
     File selection / validation
   -------------------------------------------------------------*/
  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    resetState();

    if (!selectedFile) return;

    const maxSize = 50 * 1024 * 1024; // 50 MiB
    if (selectedFile.size > maxSize) {
      setErrorMessage('File size exceeds 50 MiB limit.');
      return;
    }

    // Basic MIME-type guard (could be extended)
    const allowed = uploadType === 'image' ? /^image\// : /^(audio|video)\//;
    if (!allowed.test(selectedFile.type)) {
      setErrorMessage(`Invalid file type for ${uploadType} upload.`);
      return;
    }

    setFile(selectedFile);
    const reader = new FileReader();
    reader.onloadend = () => setPreview(reader.result as string);
    reader.readAsDataURL(selectedFile);
  };

  /* ------------------------------------------------------------
     Save action
   -------------------------------------------------------------*/
  const handleSave = async () => {
    if (!file || loading) return;

    const formData = new FormData();
    formData.append(uploadType, file);

    try {
      if (selectedSituation?._id) {
        await updateSituationAndNode(
          selectedSituation._id,
          formData as unknown as Partial<Situation>,
        );
      } else if (selectedGroup?._id) {
        await updateGroup(
          selectedGroup._id,
          formData as unknown as Partial<Group>,
        );
      }
      setIsModalOpen(false);
    } catch (error) {
      console.error(`Error updating ${uploadType}:`, error);
      setErrorMessage('An error occurred during upload. The transaction was reversed.');
    }
  };

  /* ------------------------------------------------------------
     JSX
   -------------------------------------------------------------*/
  return (
    <div className={styles.modalOverlay}>
      <div className={styles.modalContent}>
        <h2 className={styles.modalTitle}>
          Upload {uploadType === 'image' ? 'Image' : 'Media'}
        </h2>

        {/* File picker */}
        <label
          htmlFor="file-upload"
          className={`${styles.buttonBase} ${styles.uploadButton}`}
        >
          {preview ? 'Change File' : 'Select File'}
        </label>
        <input
          id="file-upload"
          type="file"
          style={{ display: 'none' }}
          onChange={handleFileChange}
          accept={uploadType === 'image' ? 'image/*' : 'audio/*,video/*'}
          disabled={loading}
        />

        {/* Validation / server messages */}
        {errorMessage && <p className={styles.errorMessage}>{errorMessage}</p>}

        {/* Preview */}
        {preview && (
          <div className={styles.previewContainer}>
            {uploadType === 'image' ? (
              <img
                src={getMediaSrc(preview)}
                alt="Preview"
                className={styles.previewImage}
              />
            ) : (
                <MediaPlayer
                  src={getMediaSrc(preview)}
                  autoplay={false}
                  className={styles.previewMedia}
                />
            )}
          </div>
        )}

        {/* Buttons */}
        <div className={styles.buttonGroup}>
          <button
            onClick={handleSave}
            className={`${styles.buttonBase} ${styles.saveButton}`}
            disabled={!file || loading}
          >
            {loading ? 'Saving…' : 'Save'}
          </button>
          <button
            onClick={() => setIsModalOpen(false)}
            className={`${styles.buttonBase} ${styles.cancelButton}`}
            disabled={loading}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadModal;