# Rich text parameters and embedded references

Several Tallyfy API parameters accept HTML rather than plain text. Inside that HTML you can reference other things: the answer somebody gave to a form field, a saved snippet, another template, or a person. This page documents what each parameter accepts, the exact markup for each kind of reference, and what happens when a reference stops resolving.

If you only need one thing from this page: a form field reference is a `span` carrying the classes `insert-variable-tag fr-deletable`, and the field's alias in double curly braces is the text inside it.

The product documentation carries the same contract in a friendlier form at
[tallyfy.com/products/pro/integrations/open-api/rich-text-references/](https://tallyfy.com/products/pro/integrations/open-api/rich-text-references/).

## Parameters that accept rich text

| Parameter | Accepts | Where it appears |
|---|---|---|
| `summary` | HTML, with embedded references | The description on a step or a task. |
| `guidance` | HTML, with embedded references | The help text on a form field. |
| `default_value` | HTML, with embedded references | The pre-filled answer on a `text` or `textarea` form field. |
| `content` | HTML, with embedded references | The body of a comment. Mentions are written here as plain text. |
| `title` | Plain text, with variables only | The name of a step, a task or a process. |

`title` is the one exception. It holds text rather than markup, so use the double curly braces on their own there and leave the `span` out.

## Send the markup, not just the braces

Sending bare `{{alias}}` with no wrapping `span` is the most common mistake, and it is hard to spot because it half works.

The API accepts it. The person doing the task sees the right value, because the substitution that swaps in the answer matches the braces alone. But the template editor recognises a variable by the `span`, not by the braces, so without it the reference shows in the editor as ordinary text. Whoever edits that template next cannot tell it is a variable, and can split or delete it without realising.

The braces make it render. The `span` makes it survive editing. Send both.

## Reference formats

### Form field variable

```html
<span class="insert-variable-tag fr-deletable" contenteditable="false">{{customer-name-4821}}</span>&nbsp;
```

Both classes are needed. `insert-variable-tag` marks it as a variable; `fr-deletable` lets a person delete the whole chip in one keystroke rather than picking it apart. `contenteditable="false"` stops the editor placing a cursor inside it.

The text inside the `span` is the field's `alias` in double curly braces. Read that alias from the API. Do not derive it from the field's label: an alias carries a unique suffix, so a guessed one will not resolve.

Whitespace inside the braces is tolerated, so `{{ alias }}` behaves the same as `{{alias}}`. A zero-width no-break space (U+FEFF) immediately either side of the braces is tolerated too, because content written by Tallyfy's older editor carries them. You do not need to send one.

Put a space after the chip. Tallyfy's own editor writes `&nbsp;`.

**Where to read the alias.** Both kinds of form field carry one, and both come back with the template. Kick-off fields are under `prerun`; step form fields are under `captures` on each step.

```bash
curl "https://go.tallyfy.com/api/organizations/{org_id}/checklists/{checklist_id}" \
  -H "Authorization: Bearer {access_token}" \
  -H "Accept: application/json" \
  -H "X-Tallyfy-Client: APIClient"
```

Each field object carries two identifiers, and they are not interchangeable. `alias` is for the variable markup above. `id` is for the inline document field below.

### System variable

Four names are reserved. They use the same `span`, with the reserved name in place of an alias.

| Name | Resolves to | Works in |
|---|---|---|
| `DATE` | The date and time the process started. | Task titles, task descriptions, process names. |
| `TEMPLATE_NAME` | The title of the template the process came from. | Task titles, task descriptions, process names. |
| `current-process-id` | The id of the process the task belongs to. | Task titles and descriptions. |
| `current-task-id` | The id of the task itself. | Task titles and descriptions. |

```html
<span class="insert-variable-tag fr-deletable" contenteditable="false">{{TEMPLATE_NAME}}</span>&nbsp;
```

The names are matched exactly. The capitalisation above is part of the format, not a house style.

### Snippet

```html
<span class="insert-snippet-tag fr-deletable" contenteditable="false" data-snippet-id="1042">[[Refund policy]]</span>&nbsp;
```

`data-snippet-id` is what resolves. The bracketed text is a label for whoever edits the template, and the snippet's current body replaces it when the text is read, so a stale label is harmless.

Snippet ids are numeric. List them from the text templates endpoint:

```bash
curl "https://go.tallyfy.com/api/organizations/{org_id}/text-templates" \
  -H "Authorization: Bearer {access_token}" \
  -H "Accept: application/json" \
  -H "X-Tallyfy-Client: APIClient"
```

### Embedded template

```html
<span class="insert-blueprint-tag fr-deletable" contenteditable="false" data-blueprint-id="{checklist_id}">[[Employee onboarding]]</span>&nbsp;
```

`data-blueprint-id` holds a template `id`, as returned by the checklists endpoint. The bracketed text is a label only. The embedded template renders expanded, so the reader sees its steps.

### Inline document field, in document templates

This one is not a reference to a field. It is the field itself, placed inside the document body for somebody to fill in.

```html
<editor-form-field
  contenteditable="false"
  data-field-id="{prerun_id}"
  data-field-label="Signature date"
  data-field-type="date"
  data-field-required="false"
  data-field-alias="signature-date-7710"
>Signature date</editor-form-field>&nbsp;
```

`data-field-id` takes the `id` exactly as the API returns it on the kick-off field object. That id stays the same as the template is edited over time, which is why it is the one that resolves. A field object carries several values that all look like plausible identifiers, so take `id` rather than picking one that looks right.

### Person and group mentions

Mentions are not HTML. They go straight into the text of a `content` or `summary` value.

```text
@[{user_id}] please review this before Friday.
```

The same form works for a group id. Read both from the members and groups endpoints.

### Guest mentions

A plus sign immediately followed by an email address:

```text
+someone@example.com is copied on this.
```

Mentioning an address that already belongs to a member of the organization mentions that member. Mentioning any other valid address **creates a guest** and sends an invitation, so treat this as a write rather than a formatting choice. Guest invites are rate limited per organization and will start returning HTTP 429.

## What happens when a reference stops resolving

Nothing validates a reference when you send it, and nothing warns anybody later. A reference stops resolving for ordinary reasons: somebody deletes the form field, archives the snippet, or removes the template.

| Reference | Behaviour when it no longer resolves |
|---|---|
| Form field variable | Replaced with an **empty string**. The reader sees a gap in the sentence. |
| System variable | A name outside the four reserved ones is treated as an unknown alias, so it is also replaced with an empty string. |
| Snippet | The reference is removed from the text. |
| Embedded template | The reference is removed from the text. This also happens when the reader lacks permission to see that template. |
| Inline document field | Renders the visible text `Error - Reference does not exist`. |
| Person or group mention | Falls back to rendering the raw id. |

Only the inline document field surfaces an error. Everywhere else the sentence closes up and reads as though it was written that way. A description sent as `Please call {{customer-name}} before Friday` renders as `Please call before Friday`.

Two consequences worth designing for:

- **Check the identifier exists before you send markup carrying it.** Afterwards nothing will tell you.
- **An empty render does not prove the reference is broken.** A form field that exists but has not been answered yet renders as nothing too, and the two cases are identical on the page.

If you copy a description between templates, remember that aliases and ids belong to the template they came from. A copied reference resolves in the original and blanks out in the copy.

## Worked example

Creating a step whose description greets somebody by name, pulls in a snippet, and mentions a colleague.

```python
import requests

headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer {access_token}',
    'X-Tallyfy-Client': 'APIClient',   # required on every request
    'Content-Type': 'application/json',
}

# The alias and the snippet id below must be read from the API first,
# not typed from memory. A reference to something that does not exist
# is accepted here and renders as nothing later.
summary = (
    '<p>Call <span class="insert-variable-tag fr-deletable" '
    'contenteditable="false">{{customer-name-4821}}</span>&nbsp;'
    'to introduce yourself.</p>'
    '<p><span class="insert-snippet-tag fr-deletable" contenteditable="false" '
    'data-snippet-id="1042">[[Refund policy]]</span>&nbsp;</p>'
    '<p>@[{user_id}] is your backup on this one.</p>'
)

response = requests.post(
    'https://go.tallyfy.com/api/organizations/{org_id}/checklists/{checklist_id}/steps',
    headers=headers,
    json={'title': 'Welcome call', 'summary': summary},
)

response.raise_for_status()
```

Building the HTML as a string is where most mistakes happen rather than in the markup itself. Every attribute quote has to survive JSON encoding, and a mangled `class` attribute produces the plain-text failure described at the top of this page.

## Checklist before you send

- Every alias and id was read from the API, not remembered or guessed.
- Variable chips carry both classes, `insert-variable-tag` and `fr-deletable`.
- Every chip carries `contenteditable="false"`.
- There is a space after each chip.
- The ids belong to the template you are writing into.
- You opened the template in Tallyfy afterwards and saw chips rather than plain text.

That last check takes ten seconds and is the only one that catches the failure this page exists to prevent.

## Reporting a problem

If a reference behaves differently from what is documented here, open an issue in this repository following the [posting guidelines](README.md#posting-guidelines). Include the exact markup you sent, with identifiers replaced by `{org_id}`, `{checklist_id}` and so on, and what rendered instead.
