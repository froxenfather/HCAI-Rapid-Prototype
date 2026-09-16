# HCAI-Rapid-Prototype

## Deliverable 2 (D2): User Modeling

**Intended Completion Time:** ~1-2 hours
*(Full team co-working synchronously and discussing answers)*

---

## List the names of all teammates:

*
*
*

## What is your Group ID:

*

---

# User Modeling

Let's think through the basics of the Human-AI Interaction that you will be designing.

Here is the figure showing **Expected Utility** from *(Horvitz 1999)*:

> **Insert or re-draw Expected Utility figure here**

---

## 1. Re-draw this same figure, and consider these terms with respect to your interface.

### a. Describe the Expected Utility of your interface. What are A and G?

**Response:**

>

### b. Describe how you interpret the meaning of these lines. How steep do you think the slope of these lines should be?

**Response:**

>

### c. Describe in your own words, what is `p*` in your interface?

**Response:**

>

---

# Shared Representation

## 2. What is the shared representation (Heer 2018) between an interface agent and direct manipulation by a user in your system?

What does this shared interface include or look like?

*(Include or re-draw an image of your paper prototype if that helps!)*

> **Insert paper prototype image here if helpful**

**Response:**

>

---

## 3. Considering your users' goals, possible actions from the system, and the shared representation, what kinds of data or information about CaringBridge users could be useful or necessary to help you infer their goals?

**Response:**

>

---

## 4. What kinds of data or information would be helpful or necessary to help you understand if your interface intervention was successful or not?

**Your answers to this question are essential for Assignment 2.**

**Response:**

>

---

# Mental Models

## 5. Try to sketch a preliminary version of how the inner workings of your implementation might actually work.

For example, a crude UML diagram would suffice.

> **Insert implementation sketch / UML diagram here**

**Response:**

>

---

## 6. What kind of a mental model do your users need to form in order to be able to interact effectively with your system?

Try to sketch out what a users' mental model would need to be.

What types of interface elements are needed to support users' mental models of your system?

> **Insert user mental model sketch here**

**Response:**

>

---

## 7. Optional

Part of being a grad student *(esp. PhD students)* is developing the skill to review recent scientific developments and apply relevant insights to your own goals and work.

Questions 7 and 8 are both fully optional, but if you are one of the students interested in research, this is a great warm-up activity to practice a research mindset.

If you would like to take this opportunity, familiarize yourself with the conference proceedings for the **ACM CHI 2026 Conference**:

https://dl.acm.org/doi/proceedings/10.1145/3772318

Identify one paper that has any kind of relevance to your interface design.

You do not need to read in depth; rather, feel free to skim and see what stands out to you.

Paste the paper title, authors, abstract, and DOI URL below.

### Paper Title

>

### Authors

>

### Abstract

>

### DOI URL

>

---

## 8. Optional

Write **2-3 sentences** describing why the methods, results, or discussion from the paper feel relevant to your design.

What could you learn from this paper that might impact either:

* How you design your intervention
* How users might feel about interacting with it

**Response:**

>

---

# CaringBridge Prototype Option Descriptions

*Re-included for reference*

When you go to create a CaringBridge page, the UI requests the following information:

* Health Condition
* Patient or Caregiver

  * If not patient, relationship to the patient
  * Primary caregiver or not

There are several key pieces of information that constitute **"Best Practices"** for a very first post on CaringBridge, including:

* Stating who the patient is and describing the health issue that is occurring
  *(e.g., accident, traumatic brain injury, specific cancer, etc.)*

* Stating who will be authoring the CaringBridge site and their relationship to the patient
  *(could be either the patient themself or a caregiver such as a close friend or family member)*

* Some light details about the patient's condition or diagnosis are a good idea so that friends and family are less likely to ask questions of the author and patient, for example:

  * Symptoms they experienced that led to the diagnosis
  * If there is no diagnosis yet, what has the doctor shared as possibilities
  * If there is already a "plan," or what the journey will look like over the next days, weeks, or months

* Disclosing essential information that can inform community responses, for example:

  * Hospital visiting hours are... or, not taking visitors right now
  * Flowers are or are not being accepted at this time, and where they should be sent
  * Whether phone calls or text messages are or are not appreciated right now

* What types of support would be helpful from the community, for example:

  * Please send prayers or kind thoughts that...
  * A fundraiser has been set up at...
  * We are in need of practical items like...
  * Food is or is not being accepted at a location
  * We are in need of support with rides to the hospital, animal or child care, household chores, etc.

* Many of these details may not be known at the time a page is created, and that's okay

* Informing friends and family if they can share the CaringBridge page with others so that there are not any questions about personal privacy concerns

* Stating what are the next steps in medical treatment

* Stating when to expect another CaringBridge update

Not all users will think ahead to these types of issues due to overwhelm or emotions running high.

Your job is to explore one of four ways that an AI-infused interface could support users to write their very first post on CaringBridge.

Here are the four options. You will be assigned one of them for your team.

---

## A. "Start from Something Similar"

The user will go through the standard CaringBridge onboarding questions listed above.

Using only this information, an initial post will be generated based off of initial posts written by similar patients.

Specific detailed information, such as proper nouns, the name of a hospital, specific visiting hours, dietary restrictions, etc., should be intentionally represented as **"blanks"** that need to be filled in by the author.

After the initial post is generated, the user can then:

* Fill in the blanks
* Adjust the length
* Adjust the style
* Adjust the tone
* Adjust the post type
* Make other edits as needed before publishing through simple on-screen options

---

## B. "Three Choices"

The author will go through the standard CaringBridge onboarding listed above.

A few additional questions should then be asked to collect information needed for a solid initial post, using simple check boxes or short text input fields so that the author does not need to be overly burdened by these questions.

Next, AI should generate **three distinct choices**, each with:

* Its own title
* Its own post body

The author can choose one of these options or click a **"Regenerate"** button to try again with three new choices.

After making their selection, the author can adjust the post as needed before posting.

---

## C. "Guided Auto-Suggestions"

The author should be guided through the creation process with straightforward suggestions, similar to auto-complete, that encourage authors to share relevant information.

Rather than generating a complete draft at the end, this option should help authors draft their posts incrementally, either:

* Sentence-by-sentence
* Paragraph-by-paragraph

The author can adjust each sentence or paragraph as they go until they have completed the post.

---

## D. "Voice-to-Post"

The author composes the post through conversation with an AI agent.

This option should use a voice-to-text API service, but it should **not** translate the conversation word-for-word.

Rather, it should convert the transcription into a coherent post.

A final draft of the post is shared after this verbal conversation, and the author can adjust it as needed before posting.

Ideally, adjustments can also be made using voice if feasible, but typed adjustments are acceptable if voice is too difficult to implement.
