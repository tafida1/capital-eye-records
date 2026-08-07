document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    const configuration =
        window.clinicalAnnotationConfiguration || {};

    const page = document.getElementById(
        "clinicalAnnotationPage"
    );

    const stage = document.getElementById(
        "clinicalAnnotationStage"
    );

    const imageContainer = document.getElementById(
        "annotationImageContainer"
    );

    const image = document.getElementById(
        "annotationSourceImage"
    );

    const canvas = document.getElementById(
        "clinicalAnnotationCanvas"
    );

    const context = canvas.getContext("2d");

    const activeIdInput = document.getElementById(
        "activeAnnotationId"
    );

    const titleInput = document.getElementById(
        "annotationTitle"
    );

    const noteInput = document.getElementById(
        "annotationClinicalNote"
    );

    const statusDisplay = document.getElementById(
        "activeAnnotationStatus"
    );

    const layerList = document.getElementById(
        "annotationLayerList"
    );

    const emptyLayers = document.getElementById(
        "annotationEmptyLayers"
    );

    const layerCount = document.getElementById(
        "annotationLayerCount"
    );

    const instruction = document.getElementById(
        "annotationStageInstruction"
    );

    const colourInput = document.getElementById(
        "annotationColour"
    );

    const strokeInput = document.getElementById(
        "annotationStrokeWidth"
    );

    const strokeValue = document.getElementById(
        "annotationStrokeValue"
    );

    const zoomDisplay = document.getElementById(
        "annotationZoomDisplay"
    );


    let annotations = [];

    const existingDataElement = document.getElementById(
        "existing-annotations-data"
    );

    if (existingDataElement) {
        try {
            annotations = JSON.parse(
                existingDataElement.textContent
            );
        } catch (error) {
            annotations = [];
        }
    }


    let objects = [];
    let undoStack = [];
    let redoStack = [];

    let activeTool = "select";
    let isDrawing = false;
    let startPoint = null;
    let currentObject = null;

    let annotationsVisible = true;
    let zoomLevel = 1;

    const minimumZoom = 0.25;
    const maximumZoom = 4;
    const zoomStep = 0.2;


    function clamp(value, minimum, maximum) {
        return Math.min(
            Math.max(value, minimum),
            maximum
        );
    }


    function cloneObjects(source) {
        return JSON.parse(
            JSON.stringify(source)
        );
    }


    function pushUndoState() {
        undoStack.push(
            cloneObjects(objects)
        );

        if (undoStack.length > 50) {
            undoStack.shift();
        }

        redoStack = [];
    }


    function canvasPoint(event) {
        const rectangle =
            canvas.getBoundingClientRect();

        return {
            x: (
                event.clientX -
                rectangle.left
            ) / rectangle.width,

            y: (
                event.clientY -
                rectangle.top
            ) / rectangle.height,
        };
    }


    function pixelPoint(normalizedPoint) {
        return {
            x: normalizedPoint.x * canvas.width,
            y: normalizedPoint.y * canvas.height,
        };
    }


    function resizeCanvas() {
        if (!image.naturalWidth || !image.naturalHeight) {
            return;
        }

        canvas.width = image.naturalWidth;
        canvas.height = image.naturalHeight;

        canvas.style.width =
            image.clientWidth + "px";

        canvas.style.height =
            image.clientHeight + "px";

        drawAllObjects();
    }


    function setDrawingStyle(annotationObject) {
        context.strokeStyle =
            annotationObject.color || "#ff0000";

        context.fillStyle =
            annotationObject.color || "#ff0000";

        context.lineWidth =
            annotationObject.strokeWidth || 3;

        context.lineCap = "round";
        context.lineJoin = "round";
    }


    function drawArrow(annotationObject) {
        const start = pixelPoint({
            x: annotationObject.startX,
            y: annotationObject.startY,
        });

        const end = pixelPoint({
            x: annotationObject.endX,
            y: annotationObject.endY,
        });

        const angle = Math.atan2(
            end.y - start.y,
            end.x - start.x
        );

        const arrowLength =
            14 + annotationObject.strokeWidth * 2;

        context.beginPath();
        context.moveTo(start.x, start.y);
        context.lineTo(end.x, end.y);
        context.stroke();

        context.beginPath();

        context.moveTo(
            end.x,
            end.y
        );

        context.lineTo(
            end.x -
                arrowLength *
                Math.cos(angle - Math.PI / 6),

            end.y -
                arrowLength *
                Math.sin(angle - Math.PI / 6)
        );

        context.lineTo(
            end.x -
                arrowLength *
                Math.cos(angle + Math.PI / 6),

            end.y -
                arrowLength *
                Math.sin(angle + Math.PI / 6)
        );

        context.closePath();
        context.fill();
    }


    function drawObject(annotationObject) {
        setDrawingStyle(
            annotationObject
        );

        if (annotationObject.type === "freehand") {
            const points =
                annotationObject.points || [];

            if (points.length < 2) {
                return;
            }

            context.beginPath();

            const first = pixelPoint(
                points[0]
            );

            context.moveTo(
                first.x,
                first.y
            );

            points.slice(1).forEach(function (point) {
                const pixel = pixelPoint(point);

                context.lineTo(
                    pixel.x,
                    pixel.y
                );
            });

            context.stroke();
            return;
        }


        if (annotationObject.type === "arrow") {
            drawArrow(annotationObject);
            return;
        }


        if (
            annotationObject.type === "rectangle" ||
            annotationObject.type === "ellipse"
        ) {
            const start = pixelPoint({
                x: annotationObject.startX,
                y: annotationObject.startY,
            });

            const end = pixelPoint({
                x: annotationObject.endX,
                y: annotationObject.endY,
            });

            const x = Math.min(
                start.x,
                end.x
            );

            const y = Math.min(
                start.y,
                end.y
            );

            const width = Math.abs(
                end.x - start.x
            );

            const height = Math.abs(
                end.y - start.y
            );

            if (annotationObject.type === "rectangle") {
                context.strokeRect(
                    x,
                    y,
                    width,
                    height
                );

                return;
            }

            context.beginPath();

            context.ellipse(
                x + width / 2,
                y + height / 2,
                Math.max(width / 2, 1),
                Math.max(height / 2, 1),
                0,
                0,
                Math.PI * 2
            );

            context.stroke();
            return;
        }


        if (annotationObject.type === "text") {
            const point = pixelPoint({
                x: annotationObject.x,
                y: annotationObject.y,
            });

            const fontSize =
                16 +
                annotationObject.strokeWidth * 2;

            context.font =
                "bold " +
                fontSize +
                "px Arial, sans-serif";

            context.fillText(
                annotationObject.text,
                point.x,
                point.y
            );
        }
    }


    function drawAllObjects() {
        context.clearRect(
            0,
            0,
            canvas.width,
            canvas.height
        );

        if (!annotationsVisible) {
            return;
        }

        objects.forEach(drawObject);

        if (currentObject) {
            drawObject(currentObject);
        }
    }


    function currentColour() {
        return colourInput.value || "#ff0000";
    }


    function currentStrokeWidth() {
        return Number(
            strokeInput.value || 3
        );
    }


    function selectTool(toolName) {
        activeTool = toolName;

        document
            .querySelectorAll(
                "[data-annotation-tool]"
            )
            .forEach(function (button) {
                button.classList.toggle(
                    "active",
                    button.dataset.annotationTool === toolName
                );
            });

        const instructions = {
            select: (
                "Select mode: inspect the image and saved markings."
            ),
            freehand: (
                "Hold and drag to draw a freehand clinical marking."
            ),
            arrow: (
                "Drag from the finding toward the direction of interest."
            ),
            rectangle: (
                "Drag to place a rectangular clinical marker."
            ),
            ellipse: (
                "Drag to circle a clinical finding."
            ),
            text: (
                "Click the image and enter a text annotation."
            ),
        };

        instruction.textContent =
            instructions[toolName] || "";
    }


    function beginDrawing(event) {
        if (
            !configuration.canEdit ||
            activeTool === "select"
        ) {
            return;
        }

        event.preventDefault();

        const point = canvasPoint(event);

        if (activeTool === "text") {
            const textValue = window.prompt(
                "Enter the clinical annotation text:"
            );

            if (!textValue) {
                return;
            }

            pushUndoState();

            objects.push({
                type: "text",
                x: point.x,
                y: point.y,
                text: textValue.slice(0, 500),
                color: currentColour(),
                strokeWidth: currentStrokeWidth(),
            });

            drawAllObjects();
            return;
        }

        pushUndoState();

        isDrawing = true;
        startPoint = point;

        if (activeTool === "freehand") {
            currentObject = {
                type: "freehand",
                points: [point],
                color: currentColour(),
                strokeWidth: currentStrokeWidth(),
            };
        } else {
            currentObject = {
                type: activeTool,
                startX: point.x,
                startY: point.y,
                endX: point.x,
                endY: point.y,
                color: currentColour(),
                strokeWidth: currentStrokeWidth(),
            };
        }
    }


    function continueDrawing(event) {
        if (!isDrawing || !currentObject) {
            return;
        }

        event.preventDefault();

        const point = canvasPoint(event);

        if (currentObject.type === "freehand") {
            currentObject.points.push(point);
        } else {
            currentObject.endX = point.x;
            currentObject.endY = point.y;
        }

        drawAllObjects();
    }


    function finishDrawing() {
        if (!isDrawing || !currentObject) {
            return;
        }

        isDrawing = false;

        objects.push(
            currentObject
        );

        currentObject = null;
        startPoint = null;

        drawAllObjects();
    }


    function undo() {
        if (!undoStack.length) {
            return;
        }

        redoStack.push(
            cloneObjects(objects)
        );

        objects = undoStack.pop();

        drawAllObjects();
    }


    function redo() {
        if (!redoStack.length) {
            return;
        }

        undoStack.push(
            cloneObjects(objects)
        );

        objects = redoStack.pop();

        drawAllObjects();
    }


    function clearCurrentDrawing() {
        if (!objects.length) {
            return;
        }

        const confirmed = window.confirm(
            "Clear every marking from the current annotation layer?"
        );

        if (!confirmed) {
            return;
        }

        pushUndoState();
        objects = [];
        drawAllObjects();
    }


    function applyZoom() {
        imageContainer.style.transform =
            "scale(" + zoomLevel + ")";

        zoomDisplay.textContent =
            Math.round(zoomLevel * 100) + "%";
    }


    function changeZoom(amount) {
        zoomLevel = clamp(
            zoomLevel + amount,
            minimumZoom,
            maximumZoom
        );

        applyZoom();
    }


    function fitImage() {
        zoomLevel = 1;
        applyZoom();
    }


    function newAnnotation() {
        activeIdInput.value = "";
        titleInput.value = "Clinical Annotation";
        noteInput.value = "";
        statusDisplay.textContent = "Unsaved";

        objects = [];
        undoStack = [];
        redoStack = [];

        drawAllObjects();
    }


    function loadAnnotation(annotation) {
        activeIdInput.value =
            annotation.id;

        titleInput.value =
            annotation.title || "";

        noteInput.value =
            annotation.clinicalNote || "";

        statusDisplay.textContent =
            annotation.statusDisplay || annotation.status;

        objects = cloneObjects(
            (
                annotation.annotationData &&
                annotation.annotationData.objects
            ) || []
        );

        undoStack = [];
        redoStack = [];

        drawAllObjects();

        document
            .querySelectorAll(".annotation-layer-item")
            .forEach(function (element) {
                element.classList.toggle(
                    "active",
                    Number(element.dataset.annotationId)
                        === Number(annotation.id)
                );
            });
    }


    function replaceOrInsertAnnotation(annotation) {
        const index = annotations.findIndex(
            function (item) {
                return Number(item.id)
                    === Number(annotation.id);
            }
        );

        if (index >= 0) {
            annotations[index] = annotation;
        } else {
            annotations.unshift(annotation);
        }

        renderAnnotationLayers();
        loadAnnotation(annotation);
    }


    function renderAnnotationLayers() {
        layerList
            .querySelectorAll(".annotation-layer-item")
            .forEach(function (element) {
                element.remove();
            });

        emptyLayers.hidden =
            annotations.length > 0;

        layerCount.textContent =
            annotations.length;

        annotations.forEach(function (annotation) {
            const item = document.createElement("article");

            item.className =
                "annotation-layer-item";

            item.dataset.annotationId =
                annotation.id;

            const statusClass =
                annotation.status === "FINAL"
                    ? "final"
                    : "draft";

            item.innerHTML =
                '<div class="annotation-layer-item-heading">' +
                    "<div>" +
                        "<strong></strong>" +
                        "<small></small>" +
                    "</div>" +
                    '<span class="annotation-layer-status ' +
                        statusClass +
                    '"></span>' +
                "</div>" +
                '<div class="annotation-layer-item-meta"></div>' +
                '<div class="annotation-layer-item-actions">' +
                    '<button type="button" ' +
                        'class="btn btn-sm btn-outline-primary ' +
                        'annotation-load-button">' +
                        "Open" +
                    "</button>" +
                    (
                        configuration.canEdit
                            ? (
                                '<button type="button" ' +
                                    'class="btn btn-sm btn-outline-danger ' +
                                    'annotation-delete-button">' +
                                    "Remove" +
                                "</button>"
                            )
                            : ""
                    ) +
                "</div>";

            item.querySelector("strong").textContent =
                annotation.title;

            item.querySelector("small").textContent =
                "Version " +
                annotation.version +
                " · " +
                annotation.updatedAt;

            item.querySelector(
                ".annotation-layer-status"
            ).textContent =
                annotation.statusDisplay;

            item.querySelector(
                ".annotation-layer-item-meta"
            ).textContent =
                "Updated by " +
                annotation.updatedBy;

            item.querySelector(
                ".annotation-load-button"
            ).addEventListener(
                "click",
                function () {
                    loadAnnotation(annotation);
                }
            );

            const deleteButton = item.querySelector(
                ".annotation-delete-button"
            );

            if (deleteButton) {
                deleteButton.addEventListener(
                    "click",
                    function () {
                        deactivateAnnotation(annotation);
                    }
                );
            }

            layerList.appendChild(item);
        });
    }


    async function saveAnnotation(status) {
        if (!configuration.canEdit) {
            return;
        }

        const title = titleInput.value.trim();

        if (!title) {
            window.alert(
                "Enter a title for this annotation."
            );

            titleInput.focus();
            return;
        }

        const payload = {
            annotationId:
                activeIdInput.value || null,

            title: title,

            clinicalNote:
                noteInput.value.trim(),

            status: status,

            annotationData: {
                schemaVersion: 1,
                objects: objects,
            },
        };

        try {
            const response = await fetch(
                configuration.saveUrl,
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken":
                            configuration.csrfToken,
                    },

                    body: JSON.stringify(payload),
                }
            );

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(
                    result.message ||
                    "The annotation could not be saved."
                );
            }

            replaceOrInsertAnnotation(
                result.annotation
            );

            window.alert(result.message);

        } catch (error) {
            window.alert(
                error.message ||
                "The annotation could not be saved."
            );
        }
    }


    async function deactivateAnnotation(annotation) {
        const confirmed = window.confirm(
            "Remove this annotation layer from active records?"
        );

        if (!confirmed) {
            return;
        }

        const url =
            configuration
                .deactivateUrlTemplate
                .replace(
                    "999999",
                    String(annotation.id)
                );

        try {
            const response = await fetch(
                url,
                {
                    method: "POST",

                    headers: {
                        "X-CSRFToken":
                            configuration.csrfToken,
                    },
                }
            );

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(
                    result.message ||
                    "The annotation could not be removed."
                );
            }

            annotations = annotations.filter(
                function (item) {
                    return Number(item.id)
                        !== Number(annotation.id);
                }
            );

            if (
                Number(activeIdInput.value)
                === Number(annotation.id)
            ) {
                newAnnotation();
            }

            renderAnnotationLayers();

        } catch (error) {
            window.alert(
                error.message ||
                "The annotation could not be removed."
            );
        }
    }


    document
        .querySelectorAll("[data-annotation-tool]")
        .forEach(function (button) {
            button.addEventListener(
                "click",
                function () {
                    selectTool(
                        button.dataset.annotationTool
                    );
                }
            );
        });


    canvas.addEventListener(
        "pointerdown",
        beginDrawing
    );

    canvas.addEventListener(
        "pointermove",
        continueDrawing
    );

    window.addEventListener(
        "pointerup",
        finishDrawing
    );


    strokeInput.addEventListener(
        "input",
        function () {
            strokeValue.textContent =
                strokeInput.value;
        }
    );


    document
        .getElementById("annotationUndoButton")
        .addEventListener("click", undo);

    document
        .getElementById("annotationRedoButton")
        .addEventListener("click", redo);

    document
        .getElementById("annotationClearButton")
        .addEventListener(
            "click",
            clearCurrentDrawing
        );

    document
        .getElementById("annotationZoomIn")
        .addEventListener(
            "click",
            function () {
                changeZoom(zoomStep);
            }
        );

    document
        .getElementById("annotationZoomOut")
        .addEventListener(
            "click",
            function () {
                changeZoom(-zoomStep);
            }
        );

    document
        .getElementById("annotationFitButton")
        .addEventListener(
            "click",
            fitImage
        );

    document
        .getElementById(
            "annotationToggleVisibility"
        )
        .addEventListener(
            "click",
            function () {
                annotationsVisible =
                    !annotationsVisible;

                drawAllObjects();
            }
        );

    document
        .getElementById(
            "annotationFullScreenButton"
        )
        .addEventListener(
            "click",
            function () {
                if (!document.fullscreenElement) {
                    page.requestFullscreen().catch(
                        function () {}
                    );

                    return;
                }

                document.exitFullscreen();
            }
        );

    document
        .getElementById(
            "newAnnotationButton"
        )
        .addEventListener(
            "click",
            newAnnotation
        );


    const draftButton = document.getElementById(
        "saveAnnotationDraftButton"
    );

    if (draftButton) {
        draftButton.addEventListener(
            "click",
            function () {
                saveAnnotation("DRAFT");
            }
        );
    }


    const finalizeButton = document.getElementById(
        "finalizeAnnotationButton"
    );

    if (finalizeButton) {
        finalizeButton.addEventListener(
            "click",
            function () {
                const confirmed = window.confirm(
                    "Finalize this clinical annotation?"
                );

                if (confirmed) {
                    saveAnnotation("FINAL");
                }
            }
        );
    }


    image.addEventListener(
        "load",
        function () {
            resizeCanvas();
            renderAnnotationLayers();

            if (annotations.length) {
                loadAnnotation(
                    annotations[0]
                );
            } else {
                newAnnotation();
            }
        }
    );


    window.addEventListener(
        "resize",
        resizeCanvas
    );


    selectTool("select");
    applyZoom();

    if (
        image.complete &&
        image.naturalWidth
    ) {
        resizeCanvas();
        renderAnnotationLayers();

        if (annotations.length) {
            loadAnnotation(
                annotations[0]
            );
        } else {
            newAnnotation();
        }
    }
});