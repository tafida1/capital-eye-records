document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    function wrapperFor(field) {
        if (!field) {
            return null;
        }

        return (
            field.closest("[data-contact-lens-field-wrapper]") ||
            field.closest(".mb-3") ||
            field.closest(".col-md-6") ||
            field.parentElement
        );
    }

    function toggleOtherField(selectElement) {
        const targetId =
            selectElement.dataset.otherTarget;

        if (!targetId) {
            return;
        }

        const targetField =
            document.getElementById(targetId);

        if (!targetField) {
            return;
        }

        const wrapper = wrapperFor(targetField);

        const shouldShow =
            String(selectElement.value).toUpperCase() ===
            "OTHER";

        if (wrapper) {
            wrapper.classList.toggle(
                "is-hidden",
                !shouldShow
            );

            wrapper.classList.add(
                "contact-lens-other-wrapper"
            );
        }

        targetField.disabled = !shouldShow;

        if (!shouldShow) {
            targetField.value = "";
        }
    }

    document
        .querySelectorAll("[data-other-target]")
        .forEach(function (selectElement) {
            toggleOtherField(selectElement);

            selectElement.addEventListener(
                "change",
                function () {
                    toggleOtherField(selectElement);
                }
            );
        });

    function toggleDependentField(controller) {
        const targetId =
            controller.dataset.detailTarget;

        if (!targetId) {
            return;
        }

        const targetField =
            document.getElementById(targetId);

        if (!targetField) {
            return;
        }

        const wrapper = wrapperFor(targetField);

        const shouldShow =
            controller.type === "checkbox"
                ? controller.checked
                : Boolean(controller.value);

        if (wrapper) {
            wrapper.classList.toggle(
                "is-hidden",
                !shouldShow
            );

            wrapper.classList.add(
                "contact-lens-dependent-wrapper"
            );
        }

        targetField.disabled = !shouldShow;

        if (!shouldShow) {
            targetField.value = "";
        }
    }

    document
        .querySelectorAll("[data-detail-target]")
        .forEach(function (controller) {
            toggleDependentField(controller);

            controller.addEventListener(
                "change",
                function () {
                    toggleDependentField(controller);
                }
            );
        });

    function toggleCylinderAxis(
        cylinderField,
        axisField
    ) {
        if (!cylinderField || !axisField) {
            return;
        }

        const numericValue =
            Number(cylinderField.value || 0);

        const hasCylinder =
            Number.isFinite(numericValue) &&
            numericValue !== 0;

        axisField.required = hasCylinder;

        const wrapper = wrapperFor(axisField);

        if (wrapper) {
            wrapper.classList.toggle(
                "contact-lens-axis-required",
                hasCylinder
            );
        }
    }

    [
        ["id_cylinder", "id_axis"],
        [
            "id_over_refraction_cylinder",
            "id_over_refraction_axis"
        ],
        [
            "id_right_cylinder",
            "id_right_axis"
        ],
        [
            "id_left_cylinder",
            "id_left_axis"
        ],
    ].forEach(function (pair) {
        const cylinderField =
            document.getElementById(pair[0]);

        const axisField =
            document.getElementById(pair[1]);

        if (!cylinderField || !axisField) {
            return;
        }

        toggleCylinderAxis(
            cylinderField,
            axisField
        );

        cylinderField.addEventListener(
            "input",
            function () {
                toggleCylinderAxis(
                    cylinderField,
                    axisField
                );
            }
        );
    });

    function toggleDesignRequirements(
        designField,
        prefix
    ) {
        if (!designField) {
            return;
        }

        const design =
            String(designField.value).toUpperCase();

        const cylinder =
            document.getElementById(
                "id_" + prefix + "cylinder"
            );

        const axis =
            document.getElementById(
                "id_" + prefix + "axis"
            );

        const addPower =
            document.getElementById(
                "id_" + prefix + "add_power"
            );

        const baseCurve =
            document.getElementById(
                "id_" + prefix + "base_curve"
            );

        if (cylinder) {
            cylinder.required =
                design === "TORIC";
        }

        if (axis) {
            axis.required =
                design === "TORIC";
        }

        if (addPower) {
            addPower.required =
                design === "MULTIFOCAL";
        }

        if (baseCurve) {
            baseCurve.required = [
                "RGP",
                "SCLERAL",
                "HYBRID"
            ].includes(design);
        }
    }

    const singleTrialDesign =
        document.getElementById(
            "id_lens_design"
        );

    if (singleTrialDesign) {
        toggleDesignRequirements(
            singleTrialDesign,
            ""
        );

        singleTrialDesign.addEventListener(
            "change",
            function () {
                toggleDesignRequirements(
                    singleTrialDesign,
                    ""
                );
            }
        );
    }

    [
        ["id_right_lens_design", "right_"],
        ["id_left_lens_design", "left_"],
    ].forEach(function (configuration) {
        const designField =
            document.getElementById(
                configuration[0]
            );

        if (!designField) {
            return;
        }

        toggleDesignRequirements(
            designField,
            configuration[1]
        );

        designField.addEventListener(
            "change",
            function () {
                toggleDesignRequirements(
                    designField,
                    configuration[1]
                );
            }
        );
    });

    document
        .querySelectorAll(
            "[data-confirm-contact-lens-action]"
        )
        .forEach(function (formElement) {
            formElement.addEventListener(
                "submit",
                function (event) {
                    const message =
                        formElement.dataset
                            .confirmContactLensAction ||
                        "Continue with this action?";

                    if (!window.confirm(message)) {
                        event.preventDefault();
                    }
                }
            );
        });

    const prescriptionForm =
        document.querySelector(
            "[data-contact-lens-prescription-form]"
        );

    if (prescriptionForm) {
        prescriptionForm.addEventListener(
            "submit",
            function (event) {
                const rightDesign =
                    document.getElementById(
                        "id_right_lens_design"
                    );

                const leftDesign =
                    document.getElementById(
                        "id_left_lens_design"
                    );

                const hasEye =
                    (
                        rightDesign &&
                        rightDesign.value
                    ) ||
                    (
                        leftDesign &&
                        leftDesign.value
                    );

                if (!hasEye) {
                    event.preventDefault();

                    window.alert(
                        "Enter Contact Lens parameters for at least one eye."
                    );
                }
            }
        );
    }
});