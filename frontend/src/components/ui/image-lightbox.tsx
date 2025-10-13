import { useState } from "react"

type ImageLightboxProps = {
  src: string
  alt: string
  className?: string
  children?: (props: { onClick: () => void }) => React.ReactNode
}

function ImageLightbox({ src, alt, className, children }: ImageLightboxProps) {
  const [isOpen, setIsOpen] = useState(false)

  const handleOpen = () => setIsOpen(true)
  const handleClose = () => setIsOpen(false)

  return (
    <>
      {children ? (
        children({ onClick: handleOpen })
      ) : (
        <img src={src} alt={alt} className={className} onClick={handleOpen} />
      )}

      {isOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/90"
          onClick={handleClose}
        >
          <button
            className="absolute right-4 top-4 text-white hover:text-gray-300"
            onClick={handleClose}
          >
            <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
          <img
            src={src}
            alt={alt}
            className="max-h-[90vh] max-w-[90vw] object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  )
}

export { ImageLightbox }
