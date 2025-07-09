// This utility provides a consistent way to resolve media sources. Whether the data
// is a local blob or a persistent URI on a remote object store, this function ensures
// that the semantic payload of a GVM element can be correctly accessed.

/**
 * Ensures that the media source path is correctly formatted.
 * If the path is not a data URI or a full HTTP/HTTPS URL,
 * it prepends the API URL to treat it as a relative path to a stored asset.
 * @param src The source string of the media.
 * @returns A fully qualified URL or the original data URI.
 */
export const getMediaSrc = (src: string | undefined | null): string => {
  if (!src) {
    return '';
  }
  if (src.startsWith('data:') || src.startsWith('http:') || src.startsWith('https://')) {
    return src;
  }
  return `${process.env.NEXT_PUBLIC_API_URL}${src}`;
};