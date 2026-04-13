# Vidit's Email Tone Guide

## General Principles

- **Direct and clear.** Lead with the point. No "I hope this email finds you well" filler.
- **Professionally warm.** Friendly but not overly casual. No emoji in formal emails.
- **Technically precise.** When discussing technical topics, use correct terminology. Don't dumb things down for technical audiences.
- **Concise.** Most emails should be 3-5 sentences. Respect the reader's time.
- **Action-oriented.** End with a clear next step or ask.

## Structure

**For short replies (1-3 sentences):**
```
[Direct answer or acknowledgment]
[Next step or ask if needed]

[Sign-off]
```

**For longer emails (product updates, proposals):**
```
[One-line context/purpose]

[Key points — bulleted if 3+]

[Clear next step or CTA]

[Sign-off]
```

## Do's

- Start with the recipient's name (no "Dear Sir/Madam")
- Use "I" and "we" naturally
- Be specific: "by Friday" not "soon", "3 features" not "several"
- End with a clear ask: "Could you confirm by Thursday?" not "Let me know your thoughts when you get a chance"

## Don'ts

- No "Just checking in" or "Following up" as subject lines — say what it's about
- No walls of text — break into paragraphs, use bullets
- No hedge language: "I was wondering if maybe..." → "Can you..."
- No unnecessary CC's mentioned in the body
- No "Please do the needful" or "Kindly revert back"

## Sign-offs

- **Default:** "Best, Vidit" or just "Vidit"
- **Casual (team):** "Thanks!" or "Cheers"
- **Formal (new client):** "Best regards, Vidit Parashar"

## Example: Client Product Email

```
Hi Sarah,

Quick update on the integration we discussed — the Gmail sync module is live
in staging. Key highlights:

- Real-time email ingestion with <2s latency
- OAuth2 flow handles token refresh automatically
- Draft creation API ready for your team's review

I'd suggest a 30-min walkthrough this week so your team can test the flow
end-to-end. Does Thursday 3 PM IST work?

Best,
Vidit
```

## Example: Reply to Team Member

```
Priya,

Good catch on the rate limit issue. I'd go with exponential backoff
starting at 1s — the Asana API docs confirm 150 req/min on free tier.

I'll update the client.py retry logic today. Can you verify it works
against the staging workspace once it's pushed?

Thanks!
Vidit
```
