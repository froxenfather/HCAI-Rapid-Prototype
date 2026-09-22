// =========================================================
// CaringBridge AI Web GUI
// =========================================================


// ---------------------------------------------------------
// Get page elements
// ---------------------------------------------------------

const form =
    document.getElementById("post-form");

const generateButton =
    document.getElementById("generate-button");

const authorRole =
    document.getElementById("author_role");

const relationshipSection =
    document.getElementById("relationship-section");

const relationshipField =
    document.getElementById("relationship_to_patient");

const caregiverField =
    document.getElementById("is_primary_caregiver");

const caregiverNameField =
    document.getElementById("primary_caregiver_name");

const resultSection =
    document.getElementById("result-section");

const generatedPost =
    document.getElementById("generated-post");

const placeholdersSection =
    document.getElementById("placeholders-section");

const placeholdersList =
    document.getElementById("placeholders-list");

const coverageSection =
    document.getElementById("coverage-section");

const coverageList =
    document.getElementById("coverage-list");

const errorMessage =
    document.getElementById("error-message");

const copyButton =
    document.getElementById("copy-button");

// Multi-step elements
const steps =
    document.querySelectorAll(".form-step");

const stepItems =
    document.querySelectorAll(".step-item");

let currentStep = 1;


// ---------------------------------------------------------
// Multi-Step Navigation logic
// ---------------------------------------------------------

function updateStepUI() {
    // Toggle form steps visibility
    steps.forEach((step) => {
        const stepNum = parseInt(step.getAttribute("data-step"), 10);
        if (stepNum === currentStep) {
            step.style.display = "block";
            step.classList.add("active-step");
        } else {
            step.style.display = "none";
            step.classList.remove("active-step");
        }
    });

    // Update progress bar step items styling
    stepItems.forEach((item, index) => {
        if (index + 1 === currentStep) {
            item.classList.add("active");
        } else {
            item.classList.remove("active");
        }
    });

    // Scroll to top of current section
    const activeSection = document.querySelector(`.form-step[data-step="${currentStep}"]`);
    if (activeSection) {
        activeSection.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }
}

// Attach click events for Next / Back buttons throughout form steps
document.addEventListener("click", (event) => {
    if (event.target.classList.contains("next-btn")) {
        clearError();

        // Validate Step 1 before advancing
        if (currentStep === 1) {
            if (!validateRequiredFields()) {
                return;
            }
        }

        if (currentStep < steps.length) {
            currentStep++;
            updateStepUI();
        }
    } else if (event.target.classList.contains("prev-btn")) {
        clearError();

        if (currentStep > 1) {
            currentStep--;
            updateStepUI();
        }
    }
});


// ---------------------------------------------------------
// Helper: get text value
// ---------------------------------------------------------

function getValue(id) {

    const element =
        document.getElementById(id);

    if (!element) {
        return null;
    }

    const value =
        element.value.trim();

    return value === ""
        ? null
        : value;
}


// ---------------------------------------------------------
// Helper: get boolean value
// ---------------------------------------------------------

function getBooleanValue(id) {

    const value =
        getValue(id);

    if (value === null) {
        return null;
    }

    if (value === "true") {
        return true;
    }

    if (value === "false") {
        return false;
    }

    return null;
}


// ---------------------------------------------------------
// Author fields
// ---------------------------------------------------------

function updateAuthorFields() {

    relationshipSection.style.display =
        "block";

    relationshipField.setAttribute(
        "required",
        "required"
    );
}


// Run when the page first loads

updateAuthorFields();


// ---------------------------------------------------------
// Author role changes
// ---------------------------------------------------------

authorRole.addEventListener(
    "change",
    () => {

        clearError();

        updateAuthorFields();
    }
);


// ---------------------------------------------------------
// Error display
// ---------------------------------------------------------

function showError(message) {

    errorMessage.textContent =
        message;

    errorMessage.style.display =
        "block";

    errorMessage.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}


function clearError() {

    errorMessage.textContent =
        "";

    errorMessage.style.display =
        "none";
}


// ---------------------------------------------------------
// Required field validation
// ---------------------------------------------------------

function validateRequiredFields() {

    const requiredFields = [
        {
            id: "author_role",
            label: "Who is writing this page?"
        },
        {
            id: "patient_name",
            label: "Patient's name"
        },
        {
            id: "health_condition",
            label: "Health condition"
        },
        {
            id: "author_name",
            label: "Your name"
        },
        {
            id: "relationship_to_patient",
            label: "Your relationship to the patient"
        }
    ];


    const missingFields = [];


    // Remove previous validation styling

    document
        .querySelectorAll(".field-error")
        .forEach((element) => {

            element.classList.remove(
                "field-error"
            );
        });


    // Check each required field

    requiredFields.forEach((field) => {

        const element =
            document.getElementById(field.id);


        if (
            !element ||
            !element.value.trim()
        ) {

            missingFields.push(field);


            if (element) {

                element.classList.add(
                    "field-error"
                );
            }
        }
    });


    // If fields are missing, show them and navigate back to step 1 if needed

    if (missingFields.length > 0) {

        if (currentStep !== 1) {
            currentStep = 1;
            updateStepUI();
        }

        const names =
            missingFields.map(
                (field) => field.label
            );


        showError(
            "Please complete the following required fields: " +
            names.join(", ") +
            "."
        );


        const firstMissing =
            document.getElementById(
                missingFields[0].id
            );


        if (firstMissing) {

            firstMissing.focus();
        }


        return false;
    }


    return true;
}


// ---------------------------------------------------------
// Build API request
// ---------------------------------------------------------

function buildRequest() {

    return {

        onboarding: {

            patient_name:
                getValue("patient_name"),

            health_condition:
                getValue("health_condition"),

            author_role:
                getValue("author_role"),

            author_name:
                getValue("author_name"),

            relationship_to_patient:
                getValue(
                    "relationship_to_patient"
                ),

            is_primary_caregiver:
                getBooleanValue(
                    "is_primary_caregiver"
                ),

            primary_caregiver_name:
                getValue(
                    "primary_caregiver_name"
                )
        },


        details: {

            event_or_symptom_context:
                getValue(
                    "event_or_symptom_context"
                ),

            diagnosis_details:
                getValue(
                    "diagnosis_details"
                ),

            hospital_name:
                getValue(
                    "hospital_name"
                ),

            treatment_plan:
                getValue(
                    "treatment_plan"
                ),

            next_medical_step:
                getValue(
                    "next_medical_step"
                ),

            visiting_information:
                getValue(
                    "visiting_information"
                ),

            flowers_information:
                getValue(
                    "flowers_information"
                ),

            phone_text_preferences:
                getValue(
                    "phone_text_preferences"
                ),

            support_needs:
                getValue(
                    "support_needs"
                ),

            fundraiser_information:
                getValue(
                    "fundraiser_information"
                ),

            food_information:
                getValue(
                    "food_information"
                ),

            transportation_support:
                getValue(
                    "transportation_support"
                ),

            child_or_pet_care_support:
                getValue(
                    "child_or_pet_care_support"
                ),

            other_support:
                getValue(
                    "other_support"
                ),

            sharing_preference:
                getValue(
                    "sharing_preference"
                ),

            next_update_timing:
                getValue(
                    "next_update_timing"
                )
        },


        preferences: {

            tone:
                getValue("tone"),

            length:
                getValue("length"),

            style:
                getValue("style")
        }
    };
}


// ---------------------------------------------------------
// Display generated response
// ---------------------------------------------------------

function displayResponse(response) {

    resultSection.style.display =
        "block";


    // Display generated post

    generatedPost.textContent =
        response.post ||
        "No draft was generated.";


    // -----------------------------------------------------
    // Display unresolved placeholders
    // -----------------------------------------------------

    placeholdersList.innerHTML =
        "";


    if (
        response.placeholders &&
        response.placeholders.length > 0
    ) {

        placeholdersSection.style.display =
            "block";


        response.placeholders.forEach(
            (placeholder) => {

                const item =
                    document.createElement("li");


                const required =
                    placeholder.required_for_publish
                        ? " — Required to publish"
                        : "";


                item.textContent =
                    `${placeholder.token} — ` +
                    `${placeholder.label}` +
                    `${required}`;


                placeholdersList.appendChild(
                    item
                );
            }
        );

    } else {

        placeholdersSection.style.display =
            "none";
    }


    // -----------------------------------------------------
    // Display coverage
    // -----------------------------------------------------

    coverageList.innerHTML =
        "";


    if (response.coverage) {

        coverageSection.style.display =
            "block";


        Object.entries(
            response.coverage
        ).forEach(
            ([category, covered]) => {

                const item =
                    document.createElement("li");


                item.textContent =
                    `${category}: ` +
                    `${covered ? "Yes" : "No"}`;


                coverageList.appendChild(
                    item
                );
            }
        );

    } else {

        coverageSection.style.display =
            "none";
    }


    // Scroll to generated result

    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


// ---------------------------------------------------------
// Form submission
// ---------------------------------------------------------

form.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();

        clearError();


        // Validate required fields

        if (!validateRequiredFields()) {
            return;
        }


        // Build request

        const request =
            buildRequest();


        // Disable button

        generateButton.disabled =
            true;

        generateButton.textContent =
            "Generating...";


        try {

            // Send request to FastAPI

            const response =
                await fetch(
                    "/api/generate",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                request
                            )
                    }
                );


            // Read response

            const data =
                await response.json();


            // Handle backend errors

            if (!response.ok) {

                const message =
                    data.detail ||
                    data.message ||
                    "Something went wrong while generating the draft.";


                throw new Error(
                    message
                );
            }


            // Display the generated draft

            displayResponse(data);

        } catch (error) {

            console.error(
                "Generation error:",
                error
            );


            showError(
                error.message ||
                "Unable to generate the draft. Please try again."
            );

        } finally {

            // Re-enable button

            generateButton.disabled =
                false;

            generateButton.textContent =
                "Generate Draft";
        }
    }
);


// ---------------------------------------------------------
// Copy generated post
// ---------------------------------------------------------

if (copyButton) {

    copyButton.addEventListener(
        "click",
        async () => {

            try {

                await navigator.clipboard.writeText(
                    generatedPost.textContent
                );


                copyButton.textContent =
                    "Copied!";


                setTimeout(
                    () => {

                        copyButton.textContent =
                            "Copy Post";

                    },
                    1500
                );

            } catch (error) {

                console.error(
                    "Copy failed:",
                    error
                );
            }
        }
    );
}