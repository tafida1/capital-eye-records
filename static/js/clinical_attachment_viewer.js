document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    const configuration =
        window.clinicalViewerConfiguration || {};

    const viewerPage = document.getElementById(
        "investigationViewerPage"
    );

    const viewerLayout = document.getElementById(
        "investigationViewerLayout"
    );

    const viewerStage = document.getElementById(
        "investigationViewerStage"
    );

    const informationPanel = document.getElementById(
        "investigationInformationPanel"
    );

    const imageViewport = document.getElementById(
        "viewerImageViewport"
    );

    const viewerImage = document.getElementById(
        "clinicalViewerImage"
    );

    const viewerPdf = document.getElementById(
        "clinicalViewerPdf"
    );

    const loadingState = document.getElementById(
        "viewerLoadingState"
    );

    const zoomDisplay = document.getElementById(
        "viewerZoomDisplay"
    );

    const zoomInButton = document.getElementById(
        "viewerZoomIn"
    );

    const zoomOutButton = document.getElementById(
        "viewerZoomOut"
    );

    const fitScreenButton = document.getElementById(
        "viewerFitScreen"
    );

    const actualSizeButton = document.getElementById(
        "viewerActualSize"
    );

    const resetButton = document.getElementById(
        "viewerReset"
    );

    const rotateLeftButton = document.getElementById(
        "viewerRotateLeft"
    );

    const rotateRightButton = document.getElementById(
        "viewerRotateRight"
    );

    const fullScreenButton = document.getElementById(
        "viewerFullScreen"
    );

    const printButton = document.getElementById(
        "viewerPrint"
    );

    const toggleInformationButton = document.getElementById(
        "viewerToggleInformation"
    );

    const closeInformationButton = document.getElementById(
        "viewerCloseInformation"
    );


    let zoomLevel = 1;
    let rotation = 0;
    let translateX = 0;
    let translateY = 0;

    let isDragging = false;
    let dragStartX = 0;
    let dragStartY = 0;
    let initialTranslateX = 0;
    let initialTranslateY = 0;

    const minimumZoom = 0.2;
    const maximumZoom = 6;
    const zoomStep = 0.2;


    function clamp(value, minimum, maximum) {
        return Math.min(
            Math.max(value, minimum),
            maximum
        );
    }


    function displayZoomLevel() {
        if (!zoomDisplay) {
            return;
        }

        zoomDisplay.textContent =
            Math.round(zoomLevel * 100) + "%";
    }


    function applyImageTransform() {
        if (!viewerImage) {
            return;
        }

        viewerImage.style.transform =
            "translate(" +
            translateX +
            "px, " +
            translateY +
            "px) " +
            "scale(" +
            zoomLevel +
            ") " +
            "rotate(" +
            rotation +
            "deg)";

        displayZoomLevel();

        if (imageViewport) {
            imageViewport.classList.toggle(
                "is-zoomed",
                zoomLevel > 1
            );
        }
    }


    function changeZoom(amount) {
        if (!viewerImage) {
            return;
        }

        zoomLevel = clamp(
            zoomLevel + amount,
            minimumZoom,
            maximumZoom
        );

        applyImageTransform();
    }


    function resetImageView() {
        zoomLevel = 1;
        rotation = 0;
        translateX = 0;
        translateY = 0;

        applyImageTransform();
    }


    function actualImageSize() {
        zoomLevel = 1;
        translateX = 0;
        translateY = 0;

        applyImageTransform();
    }


    function fitImageToScreen() {
        if (
            !viewerImage ||
            !imageViewport ||
            !viewerImage.naturalWidth ||
            !viewerImage.naturalHeight
        ) {
            return;
        }

        const availableWidth =
            imageViewport.clientWidth - 50;

        const availableHeight =
            imageViewport.clientHeight - 50;

        const imageWidth = viewerImage.naturalWidth;
        const imageHeight = viewerImage.naturalHeight;

        const normalizedRotation =
            ((rotation % 360) + 360) % 360;

        const isQuarterTurn =
            normalizedRotation === 90 ||
            normalizedRotation === 270;

        const effectiveWidth = isQuarterTurn
            ? imageHeight
            : imageWidth;

        const effectiveHeight = isQuarterTurn
            ? imageWidth
            : imageHeight;

        zoomLevel = Math.min(
            availableWidth / effectiveWidth,
            availableHeight / effectiveHeight,
            1
        );

        zoomLevel = clamp(
            zoomLevel,
            minimumZoom,
            maximumZoom
        );

        translateX = 0;
        translateY = 0;

        applyImageTransform();
    }


    function rotateImage(amount) {
        if (!viewerImage) {
            return;
        }

        rotation = (
            rotation + amount
        ) % 360;

        translateX = 0;
        translateY = 0;

        applyImageTransform();
    }


    function hideLoadingState() {
        if (loadingState) {
            loadingState.classList.add("is-hidden");
        }
    }


    function toggleInformationPanel() {
        if (!viewerLayout) {
            return;
        }

        viewerLayout.classList.toggle(
            "information-panel-hidden"
        );
    }


    function openFullScreen() {
        if (!viewerPage) {
            return;
        }

        if (!document.fullscreenElement) {
            viewerPage.requestFullscreen().catch(function () {
                // Browser denied or does not support full screen.
            });

            return;
        }

        document.exitFullscreen();
    }


    function printInvestigation() {
        if (!configuration.printUrl) {
            return;
        }

        const printWindow = window.open(
            configuration.printUrl,
            "_blank",
            "noopener"
        );

        if (!printWindow) {
            return;
        }

        printWindow.addEventListener("load", function () {
            try {
                printWindow.focus();
                printWindow.print();
            } catch (error) {
                // Some embedded PDF viewers control printing themselves.
            }
        });
    }


    if (viewerImage) {
        viewerImage.addEventListener(
            "load",
            function () {
                hideLoadingState();
                fitImageToScreen();
            }
        );

        viewerImage.addEventListener(
            "error",
            function () {
                hideLoadingState();
            }
        );
    }


    if (viewerPdf) {
        viewerPdf.addEventListener(
            "load",
            hideLoadingState
        );

        /*
         * Browser PDF viewers control their own internal zoom.
         * Hide image-only toolbar controls for PDF files.
         */
        document
            .querySelectorAll(".image-only-control")
            .forEach(function (element) {
                element.hidden = true;
            });
    }


    if (zoomInButton) {
        zoomInButton.addEventListener(
            "click",
            function () {
                changeZoom(zoomStep);
            }
        );
    }


    if (zoomOutButton) {
        zoomOutButton.addEventListener(
            "click",
            function () {
                changeZoom(-zoomStep);
            }
        );
    }


    if (fitScreenButton) {
        fitScreenButton.addEventListener(
            "click",
            fitImageToScreen
        );
    }


    if (actualSizeButton) {
        actualSizeButton.addEventListener(
            "click",
            actualImageSize
        );
    }


    if (resetButton) {
        resetButton.addEventListener(
            "click",
            resetImageView
        );
    }


    if (rotateLeftButton) {
        rotateLeftButton.addEventListener(
            "click",
            function () {
                rotateImage(-90);
            }
        );
    }


    if (rotateRightButton) {
        rotateRightButton.addEventListener(
            "click",
            function () {
                rotateImage(90);
            }
        );
    }


    if (fullScreenButton) {
        fullScreenButton.addEventListener(
            "click",
            openFullScreen
        );
    }


    if (printButton) {
        printButton.addEventListener(
            "click",
            printInvestigation
        );
    }


    if (toggleInformationButton) {
        toggleInformationButton.addEventListener(
            "click",
            toggleInformationPanel
        );
    }


    if (closeInformationButton) {
        closeInformationButton.addEventListener(
            "click",
            toggleInformationPanel
        );
    }


    /*
     * Mouse-wheel zoom
     */
    if (imageViewport) {
        imageViewport.addEventListener(
            "wheel",
            function (event) {
                if (!viewerImage) {
                    return;
                }

                event.preventDefault();

                changeZoom(
                    event.deltaY < 0
                        ? zoomStep
                        : -zoomStep
                );
            },
            {
                passive: false,
            }
        );
    }


    /*
     * Click-and-drag panning
     */
    if (imageViewport) {
        imageViewport.addEventListener(
            "mousedown",
            function (event) {
                if (!viewerImage) {
                    return;
                }

                isDragging = true;

                dragStartX = event.clientX;
                dragStartY = event.clientY;

                initialTranslateX = translateX;
                initialTranslateY = translateY;

                imageViewport.classList.add(
                    "is-dragging"
                );
            }
        );

        window.addEventListener(
            "mousemove",
            function (event) {
                if (!isDragging) {
                    return;
                }

                translateX =
                    initialTranslateX +
                    event.clientX -
                    dragStartX;

                translateY =
                    initialTranslateY +
                    event.clientY -
                    dragStartY;

                applyImageTransform();
            }
        );

        window.addEventListener(
            "mouseup",
            function () {
                isDragging = false;

                imageViewport.classList.remove(
                    "is-dragging"
                );
            }
        );
    }


    /*
     * Touch panning for mobile/tablet.
     */
    let touchStartX = 0;
    let touchStartY = 0;

    if (imageViewport) {
        imageViewport.addEventListener(
            "touchstart",
            function (event) {
                if (
                    !viewerImage ||
                    event.touches.length !== 1
                ) {
                    return;
                }

                isDragging = true;

                touchStartX =
                    event.touches[0].clientX;

                touchStartY =
                    event.touches[0].clientY;

                initialTranslateX = translateX;
                initialTranslateY = translateY;
            },
            {
                passive: true,
            }
        );

        imageViewport.addEventListener(
            "touchmove",
            function (event) {
                if (
                    !isDragging ||
                    event.touches.length !== 1
                ) {
                    return;
                }

                translateX =
                    initialTranslateX +
                    event.touches[0].clientX -
                    touchStartX;

                translateY =
                    initialTranslateY +
                    event.touches[0].clientY -
                    touchStartY;

                applyImageTransform();
            },
            {
                passive: true,
            }
        );

        imageViewport.addEventListener(
            "touchend",
            function () {
                isDragging = false;
            }
        );
    }


    /*
     * Keyboard shortcuts
     */
    document.addEventListener(
        "keydown",
        function (event) {
            const activeElement =
                document.activeElement;

            const isTyping =
                activeElement &&
                (
                    activeElement.tagName === "INPUT" ||
                    activeElement.tagName === "TEXTAREA" ||
                    activeElement.tagName === "SELECT"
                );

            if (isTyping) {
                return;
            }

            switch (event.key) {
                case "+":
                case "=":
                    event.preventDefault();
                    changeZoom(zoomStep);
                    break;

                case "-":
                case "_":
                    event.preventDefault();
                    changeZoom(-zoomStep);
                    break;

                case "0":
                    event.preventDefault();
                    resetImageView();
                    break;

                case "f":
                case "F":
                    event.preventDefault();
                    fitImageToScreen();
                    break;

                case "r":
                case "R":
                    event.preventDefault();
                    rotateImage(90);
                    break;

                case "ArrowLeft":
                    if (configuration.previousUrl) {
                        window.location.href =
                            configuration.previousUrl;
                    }
                    break;

                case "ArrowRight":
                    if (configuration.nextUrl) {
                        window.location.href =
                            configuration.nextUrl;
                    }
                    break;

                default:
                    break;
            }
        }
    );


    window.addEventListener(
        "resize",
        function () {
            if (
                viewerImage &&
                zoomLevel <= 1
            ) {
                fitImageToScreen();
            }
        }
    );


    document.addEventListener(
        "fullscreenchange",
        function () {
            if (!viewerPage) {
                return;
            }

            viewerPage.classList.toggle(
                "is-fullscreen",
                Boolean(document.fullscreenElement)
            );

            if (viewerImage) {
                window.setTimeout(
                    fitImageToScreen,
                    100
                );
            }
        }
    );


    /*
     * If the image was already loaded from browser cache before the
     * event listener was attached, initialize it immediately.
     */
    if (
        viewerImage &&
        viewerImage.complete &&
        viewerImage.naturalWidth
    ) {
        hideLoadingState();
        fitImageToScreen();
    }

    displayZoomLevel();
});