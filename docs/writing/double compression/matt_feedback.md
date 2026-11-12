I read the NCEMS draft. I think it's heading in the right direction. From a writing perspective, the two biggest problems I currently see is (1) it looks like AI-writing (and the Pangram report puts it at 78% AI writing) (2) it lacks engagement with the emerging field of papers on automated science and automated review. I've attached the PanGram report and another automated review showing the key citations to add (including Dashun's latest PNAS paper) plus rhetorical approaches you may want to consider. Fwiw, I think the AI-like writing obscures the analysis and it's not as sharp, simple, and straightforward as the results could be.

I really like this idea which I find central to the paper: "AI can remain within the same broad scientific domains as humans while undersampling the distinctive edges of their idea space, and AI reviewers can cover much of the semantic territory of human review while supplying less independent judgment" and I think Figure 3 A is rocking showing the human coverage is higher than AI coverage (but I do worry that this may be a sample size effect here and a different 23 human submissions would not be 4.94)
 
From an analysis perspective, here's my human (non-AI) feedback:

1. Fig 3C in bottom right suggests there are 4-5 human ideas with no AI match and 2 AI ideas with no human match. Likewise Result A claims: AI generated fewer distinct ideas. If you can make this claim, then I assume you can make a claim: There are X unique human ideas among the 23 proposals and Y unique AI ideas among the 23 (X among the 69) AI proposals. Likewise, there are N ideas proposed by 2 humans, 3 humans, 4 humans etc. and M ideas proposed by 2 AI, 3 AI etc.
2. Richness is measured via Vendi, which is implied for set's similarity structure but it's opaque... can you offer a concrete example showing how a proposal is transformed into a richness score? This feels like it's not grounded and the analysis is AI-generated (I'm not claiming it is, but that's my feeling as a reader)
3. I'd like to know how number of distinct ideas (related to the Vendi score) scales with number of proposals generated? How many proposals do you have to generative to have hit the same amount of ideas as humans.
4. How good are AI ideas? Can we get review scores for a subset so we can compare quality?
5. Are the distinctive human edges highly scored?
6. What is the reviewer prompt? This matters a ton for the expected diversity of the response. For example, what if you had AI personas focus only only (a) novelty (b) feasibility (c) some weird particularity (d) engagement with the most hyped topics (e) generalizability (f) clinical relevant (g) mechanistic insight (h) reproducibility (i) risk-benefit profile (j) validity of measurement then if each persona focused on those things independently we should expect diversity. My point here is the outcome depends on how you choose to generate reviews with AI, so you need to steelman this by giving the most diversity expecting prompt you can come up with

  

Other details:

1. What year are the NCEMs proposals from?
2. Can you give more details on the one-at-a-time condition? Is it like high temperature? I think this isn't as much of a steelman as giving a generated proposal and saying be different, then givngn 2 generated proposals and saying be different all the way up to 23. Can you run that?
3. More details on persona conditions -- how are the 5 titles and abstracts chosen?
4. What's the prompt for style normalization? That should be included here for transparency. When style normalizing how many characters are these proposals?
5. Is BioLinkBERT the right model here? Should we be using a commercial embedding or BioClinicalModernBert
6. Is there an SI, I see it referenced but do not see it.
