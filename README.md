# HCAI-Rapid-Prototype

## Deliverable 2 (D2): User Modeling

**Intended Completion Time:** ~1-2 hours
*(Full team co-working synchronously and discussing answers)*

---

## List the names of all teammates:

* Ryan F
* Matthew M
* Kevin B

## What is your Group ID:

* A2

---

# User Modeling

Let's think through the basics of the Human-AI Interaction that you will be designing.

Here is the figure showing **Expected Utility** from *(Horvitz 1999)*:

<img width="334" height="215" alt="yearp" src="https://github.com/user-attachments/assets/abc8a4d0-cf20-4491-9112-9939939b4028" />

## 1. Re-draw this same figure, and consider these terms with respect to your interface.

### a. Describe the Expected Utility of your interface. What are A and G?

**Response:**

> The expected utility of our interface is similar to the calculation of "is the risk worth the reward". When AI contemplates whether to jump in, it looks at two possible outcomes, jumping in to help you correctly or jumping in incorrectly and interrupting your workflow. Since the AI never knows your mind with 100% certainty, it multiplies the chance it's right by the reward, and balances that against the chance it's wrong times the penalty, which combined score is the Expected Utility. Here, G is what the user truly wants, which is the user's internal need or goal the AI can not see directly. 'A' is the AI's physical move, whether it is actually stepping in to do something. With this, Expected Utility is the 'worth it' score. The AI calculates whether jumping in does more good than harm by balancing the reward of being right against the cost of being wrong.

### b. Describe how you interpret the meaning of these lines. How steep do you think the slope of these lines should be?

**Response:**

> The lines track user satisfaction depending on whether the AI decides to step in or leave you be. The 'Action' line rises as it becomes more likely for the user to actually want help, whereas the 'No Action' line falls because working alone can become frustrating when assistance is needed. The steepness of the slopes depends on the stakes of the interaction. The more annoying an unwanted interruption is, the steeper the line needs to be.

### c. Describe in your own words, what is `p*` in your interface?

**Response:**

> I believe that p* in simpler terms is the tipping-point confidence number. It is the exact percentage that crosses the threshold where AI would decide to step in or not. If the AI's confidence is below p*, the penalty of an unwanted interruption outweighs the benefit, so it stays silent. Once confidence crosses above p*, the value of helping is greater, so it takes action.

---

# Shared Representation

## 2. What is the shared representation (Heer 2018) between an interface agent and direct manipulation by a user in your system?

The shared representation in our system is the generated CaringBridge post itself. The AI creates an example first post based on the user's onboarding information and first posts from users with similar onboarding information. This gives the user a starting point rather than requiring them to begin with a blank page.

Information that the AI cannot safely or accurately determine, such as names, hospital information, visitation hours, and other specific details, will be represented as highlighted brackets or placeholders within the post. The user can directly interact with these placeholders by clicking on them and either entering information into a text box, selecting an option from a menu, or using another input depending on the type of information needed.

The user can also directly edit any of the AI-generated surrounding text. This means that both the AI and the user are working on the same representation: the post draft. The AI provides the initial structure and example content, while the user fills in missing information, changes wording, and ultimately decides what is included before publishing.

Finally, 
The user is not able to post untill all the brackets are filled in, or deleted (which require them to "Are you sure" a question box)
---

## 3. Considering your users' goals, possible actions from the system, and the shared representation, what kinds of data or information about CaringBridge users could be useful or necessary to help you infer their goals?

The most important information would be the information already collected during CaringBridge onboarding. This includes the user's health condition, whether they are the patient or a caregiver, their relationship to the patient if applicable, and whether they are the primary caregiver. This information can help the system identify similar first posts and generate a starting point that is more relevant to that user's situation. This is what will be fed into the AI to generate a new post after all. It could also be useful to know that this is the user's first post, since our intervention is specifically designed to help users who may be intimidated or unsure about how to begin. The system could also use information about how the user interacts with the generated post, such as which placeholders they fill in, what generated text they edit or remove, and whether they choose to use the AI-assisted creator at all.

The system should avoid attempting to infer specific information that was never provided, especially proper nouns, medical details, visitation information, or other identifiable information. Instead, those pieces of information should remain as placeholders for the user to provide directly.

---

## 4. What kinds of data or information would be helpful or necessary to help you understand if your interface intervention was successful or not?

**Your answers to this question are essential for Assignment 2.**

To understand whether the intervention was successful, we would really want to measure both whether users were able to complete their first post and whether the AI-generated starting point actually made that process easier.

Useful information could include:

- Whether users choose the AI-assisted option or go directly to the normal post creator.
- Whether users who select the AI-assisted option successfully complete and publish their first post.
- How long it takes users to create their first post.
- How many of the generated placeholders users successfully fill in.
- How much of the AI-generated text users keep, edit, or completely remove.
- Whether users return to the normal post creator instead of finishing the AI-assisted version.
- Whether users use the AI-assisted creator again after their first post through the optional link in the normal post creator.
- How confident users feel about their final post.
- Whether users feel that the generated example made writing their first post easier or less intimidating.
- Whether users feel that they still had control over the wording and information included in the final post.

These measurements would help us determine not only whether users completed the task, but also whether the intervention reduced the difficulty of starting a first post without taking control away from the user. Overall seeing how much the users interacted or changed the pregiven prompt is our definite measure of success!

Possibly could look into a "rating system" as well!

---

# Mental Models

## 5. Try to sketch a preliminary version of how the inner workings of your implementation might actually work.

For example, a crude UML diagram would suffice.

<img width="1757" height="1393" alt="image" src="https://github.com/user-attachments/assets/73f28eec-1afd-4bc5-881c-038794cfcbda" />

**Response:**
Our proposed solution involves taking the user's information and building a mad libs-esque response where they can populate the fields in the initial post themselves.
This will be offered via pop-up on the first post, and will be available via a prompt at the bottom of the text entry field for later posts
>

---

## 6. What kind of a mental model do your users need to form in order to be able to interact effectively with your system?

Try to sketch out what a users' mental model would need to be.

What types of interface elements are needed to support users' mental models of your system?

<img width="1659" height="806" alt="image" src="https://github.com/user-attachments/assets/4fca47ca-1a1b-49e9-83b5-7c09baa3ba77" />

**Response:**
Our interface is simple enough that it can be powered by pop-ups, buttons, and text entry fields.

The mental model we wish to cultivate is that Caring Bridge's AI is like a helpful friend who has helped draft many initial posts and can help you too!
The AI will know only what you tell it, but can use this information to help make as good of a post as possible. 
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
