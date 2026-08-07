document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    const configuration =
        window.clinicalComparisonConfiguration || {};

    const comparisonPage = document.getElementById(
        "clinicalComparisonPage"
    );

    const comparisonLayout = document.getElementById(
        "clinicalComparisonLayout"
    );

    const synchronizeInput = document.getElementById(
        "comparisonSynchronize"
    );

    const zoomDisplay = document.getElementById(
        "comparisonZoomDisplay"
    );

    const leftImage = document.querySelector(
        '[data-comparison-image="left"]'
    );

    const rightImage = document.querySelector(
        '[data-comparison-image="right"]'
    );

    const leftViewport = document.querySelector(
        '[data-comparison-viewport="left"]'
    );

    const rightViewport = document.querySelector(
        '[data-comparison-viewport="right"]'
    );

    const states = {
        left: {
            image: leftImage,
            viewport: leftViewport,
            zoom: 1,
            rotation: 0,
            x: 0,
            y: 0,
            dragging: false,
            startX: 0,
            startY: 0,
            originalX: 0,
            originalY: 0,
        },
        right: {
            image: rightImage,
            viewport: rightViewport,
            zoom: 1,
            rotation: 0,
            x: 0,
            y: 0,
            dragging: false,
            startX: 0,
            startY: 0,
            originalX: 0,
            originalY: 0,
        },
    };

    const minimumZoom = 0.2;
    const maximumZoom = 6;
    const zoomStep = 0.2;

    let activeSide = "left";


    function clamp(value, minimum, maximum) {
        return Math.min(
            Math.max(value, minimum),
            maximum
        );
    }


    function synchronized() {
        return Boolean(
            synchronizeInput &&
            synchronizeInput.checked &&
            leftImage &&
            rightImage
        );
    }


    function updateZoomDisplay() {
        if (!zoomDisplay) {
            return;
        }

        zoomDisplay.textContent =
            Math.round(
                states[activeSide].zoom * 100
            ) + "%";
    }


    function applyTransform(side) {
        const state = states[side];

        if (!state.image) {
            return;
        }

        state.image.style.transform =
            "translate(" +
            state.x +
            "px, " +
            state.y +
            "px) " +
            "scale(" +
            state.zoom +
            ") " +
            "rotate(" +
            state.rotation +
            "deg)";
    }


    function applyAllTransforms() {
        applyTransform("left");
        applyTransform("right");
        updateZoomDisplay();
    }


    function updateValue(side, property, value) {
        states[side][property] = value;

        if (synchronized()) {
            const otherSide =
                side === "left"
                    ? "right"
                    : "left";

            states[otherSide][property] = value;
        }

        applyAllTransforms();
    }


    function changeZoom(amount) {
        const currentZoom =
            states[activeSide].zoom;

        const newZoom = clamp(
            currentZoom + amount,
            minimumZoom,
            maximumZoom
        );

        updateValue(
            activeSide,
            "zoom",
            newZoom
        );
    }


    function rotate(amount) {
        const newRotation =
            (
                states[activeSide].rotation +
                amount
            ) % 360;

        updateValue(
            activeSide,
            "rotation",
            newRotation
        );
    }


    function resetSide(side) {
        states[side].zoom = 1;
        states[side].rotation = 0;
        states[side].x = 0;
        states[side].y = 0;
    }


    function resetComparison() {
        resetSide("left");
        resetSide("right");
        applyAllTransforms();
    }


    function fitSide(side) {
        const state = states[side];

        if (
            !state.image ||
            !state.viewport ||
            !state.image.naturalWidth ||
            !state.image.naturalHeight
        ) {
            return;
        }

        const availableWidth =
            state.viewport.clientWidth - 30;

        const availableHeight =
            state.viewport.clientHeight - 30;

        state.zoom = Math.min(
            availableWidth /
                state.image.naturalWidth,
            availableHeight /
                state.image.naturalHeight,
            1
        );

        state.zoom = clamp(
            state.zoom,
            minimumZoom,
            maximumZoom
        );

        state.x = 0;
        state.y = 0;
    }


    function fitComparison() {
        fitSide("left");
        fitSide("right");

        if (synchronized() && leftImage && rightImage) {
            const synchronizedZoom = Math.min(
                states.left.zoom,
                states.right.zoom
            );

            states.left.zoom =
                synchronizedZoom;

            states.right.zoom =
                synchronizedZoom;
        }

        applyAllTransforms();
    }


    function configureViewport(side) {
        const state = states[side];

        if (!state.viewport || !state.image) {
            return;
        }

        state.viewport.addEventListener(
            "mouseenter",
            function () {
                activeSide = side;
                updateZoomDisplay();
            }
        );

        state.viewport.addEventListener(
            "wheel",
            function (event) {
                event.preventDefault();
                activeSide = side;

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

        state.viewport.addEventListener(
            "mousedown",
            function (event) {
                activeSide = side;
                state.dragging = true;

                state.startX = event.clientX;
                state.startY = event.clientY;

                state.originalX = state.x;
                state.originalY = state.y;

                state.viewport.classList.add(
                    "is-dragging"
                );
            }
        );

        window.addEventListener(
            "mousemove",
            function (event) {
                if (!state.dragging) {
                    return;
                }

                const newX =
                    state.originalX +
                    event.clientX -
                    state.startX;

                const newY =
                    state.originalY +
                    event.clientY -
                    state.startY;

                state.x = newX;
                state.y = newY;

                if (synchronized()) {
                    const otherSide =
                        side === "left"
                            ? "right"
                            : "left";

                    states[otherSide].x = newX;
                    states[otherSide].y = newY;
                }

                applyAllTransforms();
            }
        );

        window.addEventListener(
            "mouseup",
            function () {
                state.dragging = false;

                state.viewport.classList.remove(
                    "is-dragging"
                );
            }
        );

        state.image.addEventListener(
            "load",
            fitComparison
        );
    }


    configureViewport("left");
    configureViewport("right");


    const zoomIn = document.getElementById(
        "comparisonZoomIn"
    );

    const zoomOut = document.getElementById(
        "comparisonZoomOut"
    );

    const fitButton = document.getElementById(
        "comparisonFitButton"
    );

    const resetButton = document.getElementById(
        "comparisonResetButton"
    );

    const rotateLeft = document.getElementById(
        "comparisonRotateLeft"
    );

    const rotateRight = document.getElementById(
        "comparisonRotateRight"
    );

    const swapButton = document.getElementById(
        "comparisonSwapButton"
    );

    const fullScreenButton = document.getElementById(
        "comparisonFullScreenButton"
    );


    if (zoomIn) {
        zoomIn.addEventListener(
            "click",
            function () {
                changeZoom(zoomStep);
            }
        );
    }


    if (zoomOut) {
        zoomOut.addEventListener(
            "click",
            function () {
                changeZoom(-zoomStep);
            }
        );
    }


    if (fitButton) {
        fitButton.addEventListener(
            "click",
            fitComparison
        );
    }


    if (resetButton) {
        resetButton.addEventListener(
            "click",
            resetComparison
        );
    }


    if (rotateLeft) {
        rotateLeft.addEventListener(
            "click",
            function () {
                rotate(-90);
            }
        );
    }


    if (rotateRight) {
        rotateRight.addEventListener(
            "click",
            function () {
                rotate(90);
            }
        );
    }


    if (swapButton && comparisonLayout) {
        swapButton.addEventListener(
            "click",
            function () {
                comparisonLayout.classList.toggle(
                    "comparison-sides-swapped"
                );
            }
        );
    }


    if (
        fullScreenButton &&
        comparisonPage
    ) {
        fullScreenButton.addEventListener(
            "click",
            function () {
                if (!document.fullscreenElement) {
                    comparisonPage
                        .requestFullscreen()
                        .catch(function () {
                            // Fullscreen unavailable or denied.
                        });

                    return;
                }

                document.exitFullscreen();
            }
        );
    }


    document.addEventListener(
        "keydown",
        function (event) {
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
                    resetComparison();
                    break;

                case "f":
                case "F":
                    event.preventDefault();
                    fitComparison();
                    break;

                case "r":
                case "R":
                    event.preventDefault();
                    rotate(90);
                    break;

                default:
                    break;
            }
        }
    );


    if (
        leftImage &&
        leftImage.complete &&
        rightImage &&
        rightImage.complete
    ) {
        fitComparison();
    }

    updateZoomDisplay();
});document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    const configuration =
        window.clinicalComparisonConfiguration || {};

    const comparisonPage = document.getElementById(
        "clinicalComparisonPage"
    );

    const comparisonLayout = document.getElementById(
        "clinicalComparisonLayout"
    );

    const synchronizeInput = document.getElementById(
        "comparisonSynchronize"
    );

    const zoomDisplay = document.getElementById(
        "comparisonZoomDisplay"
    );

    const leftImage = document.querySelector(
        '[data-comparison-image="left"]'
    );

    const rightImage = document.querySelector(
        '[data-comparison-image="right"]'
    );

    const leftViewport = document.querySelector(
        '[data-comparison-viewport="left"]'
    );

    const rightViewport = document.querySelector(
        '[data-comparison-viewport="right"]'
    );

    const states = {
        left: {
            image: leftImage,
            viewport: leftViewport,
            zoom: 1,
            rotation: 0,
            x: 0,
            y: 0,
            dragging: false,
            startX: 0,
            startY: 0,
            originalX: 0,
            originalY: 0,
        },
        right: {
            image: rightImage,
            viewport: rightViewport,
            zoom: 1,
            rotation: 0,
            x: 0,
            y: 0,
            dragging: false,
            startX: 0,
            startY: 0,
            originalX: 0,
            originalY: 0,
        },
    };

    const minimumZoom = 0.2;
    const maximumZoom = 6;
    const zoomStep = 0.2;

    let activeSide = "left";


    function clamp(value, minimum, maximum) {
        return Math.min(
            Math.max(value, minimum),
            maximum
        );
    }


    function synchronized() {
        return Boolean(
            synchronizeInput &&
            synchronizeInput.checked &&
            leftImage &&
            rightImage
        );
    }


    function updateZoomDisplay() {
        if (!zoomDisplay) {
            return;
        }

        zoomDisplay.textContent =
            Math.round(
                states[activeSide].zoom * 100
            ) + "%";
    }


    function applyTransform(side) {
        const state = states[side];

        if (!state.image) {
            return;
        }

        state.image.style.transform =
            "translate(" +
            state.x +
            "px, " +
            state.y +
            "px) " +
            "scale(" +
            state.zoom +
            ") " +
            "rotate(" +
            state.rotation +
            "deg)";
    }


    function applyAllTransforms() {
        applyTransform("left");
        applyTransform("right");
        updateZoomDisplay();
    }


    function updateValue(side, property, value) {
        states[side][property] = value;

        if (synchronized()) {
            const otherSide =
                side === "left"
                    ? "right"
                    : "left";

            states[otherSide][property] = value;
        }

        applyAllTransforms();
    }


    function changeZoom(amount) {
        const currentZoom =
            states[activeSide].zoom;

        const newZoom = clamp(
            currentZoom + amount,
            minimumZoom,
            maximumZoom
        );

        updateValue(
            activeSide,
            "zoom",
            newZoom
        );
    }


    function rotate(amount) {
        const newRotation =
            (
                states[activeSide].rotation +
                amount
            ) % 360;

        updateValue(
            activeSide,
            "rotation",
            newRotation
        );
    }


    function resetSide(side) {
        states[side].zoom = 1;
        states[side].rotation = 0;
        states[side].x = 0;
        states[side].y = 0;
    }


    function resetComparison() {
        resetSide("left");
        resetSide("right");
        applyAllTransforms();
    }


    function fitSide(side) {
        const state = states[side];

        if (
            !state.image ||
            !state.viewport ||
            !state.image.naturalWidth ||
            !state.image.naturalHeight
        ) {
            return;
        }

        const availableWidth =
            state.viewport.clientWidth - 30;

        const availableHeight =
            state.viewport.clientHeight - 30;

        state.zoom = Math.min(
            availableWidth /
                state.image.naturalWidth,
            availableHeight /
                state.image.naturalHeight,
            1
        );

        state.zoom = clamp(
            state.zoom,
            minimumZoom,
            maximumZoom
        );

        state.x = 0;
        state.y = 0;
    }


    function fitComparison() {
        fitSide("left");
        fitSide("right");

        if (synchronized() && leftImage && rightImage) {
            const synchronizedZoom = Math.min(
                states.left.zoom,
                states.right.zoom
            );

            states.left.zoom =
                synchronizedZoom;

            states.right.zoom =
                synchronizedZoom;
        }

        applyAllTransforms();
    }


    function configureViewport(side) {
        const state = states[side];

        if (!state.viewport || !state.image) {
            return;
        }

        state.viewport.addEventListener(
            "mouseenter",
            function () {
                activeSide = side;
                updateZoomDisplay();
            }
        );

        state.viewport.addEventListener(
            "wheel",
            function (event) {
                event.preventDefault();
                activeSide = side;

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

        state.viewport.addEventListener(
            "mousedown",
            function (event) {
                activeSide = side;
                state.dragging = true;

                state.startX = event.clientX;
                state.startY = event.clientY;

                state.originalX = state.x;
                state.originalY = state.y;

                state.viewport.classList.add(
                    "is-dragging"
                );
            }
        );

        window.addEventListener(
            "mousemove",
            function (event) {
                if (!state.dragging) {
                    return;
                }

                const newX =
                    state.originalX +
                    event.clientX -
                    state.startX;

                const newY =
                    state.originalY +
                    event.clientY -
                    state.startY;

                state.x = newX;
                state.y = newY;

                if (synchronized()) {
                    const otherSide =
                        side === "left"
                            ? "right"
                            : "left";

                    states[otherSide].x = newX;
                    states[otherSide].y = newY;
                }

                applyAllTransforms();
            }
        );

        window.addEventListener(
            "mouseup",
            function () {
                state.dragging = false;

                state.viewport.classList.remove(
                    "is-dragging"
                );
            }
        );

        state.image.addEventListener(
            "load",
            fitComparison
        );
    }


    configureViewport("left");
    configureViewport("right");


    const zoomIn = document.getElementById(
        "comparisonZoomIn"
    );

    const zoomOut = document.getElementById(
        "comparisonZoomOut"
    );

    const fitButton = document.getElementById(
        "comparisonFitButton"
    );

    const resetButton = document.getElementById(
        "comparisonResetButton"
    );

    const rotateLeft = document.getElementById(
        "comparisonRotateLeft"
    );

    const rotateRight = document.getElementById(
        "comparisonRotateRight"
    );

    const swapButton = document.getElementById(
        "comparisonSwapButton"
    );

    const fullScreenButton = document.getElementById(
        "comparisonFullScreenButton"
    );


    if (zoomIn) {
        zoomIn.addEventListener(
            "click",
            function () {
                changeZoom(zoomStep);
            }
        );
    }


    if (zoomOut) {
        zoomOut.addEventListener(
            "click",
            function () {
                changeZoom(-zoomStep);
            }
        );
    }


    if (fitButton) {
        fitButton.addEventListener(
            "click",
            fitComparison
        );
    }


    if (resetButton) {
        resetButton.addEventListener(
            "click",
            resetComparison
        );
    }


    if (rotateLeft) {
        rotateLeft.addEventListener(
            "click",
            function () {
                rotate(-90);
            }
        );
    }


    if (rotateRight) {
        rotateRight.addEventListener(
            "click",
            function () {
                rotate(90);
            }
        );
    }


    if (swapButton && comparisonLayout) {
        swapButton.addEventListener(
            "click",
            function () {
                comparisonLayout.classList.toggle(
                    "comparison-sides-swapped"
                );
            }
        );
    }


    if (
        fullScreenButton &&
        comparisonPage
    ) {
        fullScreenButton.addEventListener(
            "click",
            function () {
                if (!document.fullscreenElement) {
                    comparisonPage
                        .requestFullscreen()
                        .catch(function () {
                            // Fullscreen unavailable or denied.
                        });

                    return;
                }

                document.exitFullscreen();
            }
        );
    }


    document.addEventListener(
        "keydown",
        function (event) {
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
                    resetComparison();
                    break;

                case "f":
                case "F":
                    event.preventDefault();
                    fitComparison();
                    break;

                case "r":
                case "R":
                    event.preventDefault();
                    rotate(90);
                    break;

                default:
                    break;
            }
        }
    );


    if (
        leftImage &&
        leftImage.complete &&
        rightImage &&
        rightImage.complete
    ) {
        fitComparison();
    }

    updateZoomDisplay();
});