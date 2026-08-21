<div align="center">

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/canticle-profile-hero.png?v=ghost-articulated-1">
  <source type="image/gif" srcset="./assets/canticle-profile-hero.gif?v=ghost-articulated-1">
  <img src="./assets/canticle-profile-hero.png?v=ghost-articulated-1" alt="BlackhatShiftey with Ghost—the anime girl and her cute cat-like spirit forms—in the Canticle RGB research style" width="100%">
</picture>

</div>

```text
blackhatshiftey@canticle:~$ ./research-station --status

operator   BlackhatShiftey
company    Canticle
form       solo-founded AI research group
channel    Canticle AI Research
mission    investigate AI behavior through safe, open systems
programs   LLMs · transformers · evaluation harnesses
           memory architecture · affective mapping
           steganography · safe AI-to-AI languages · education
method     hypothesize · instrument · falsify · reproduce
status     active / conclusions bounded by available evidence
```

Canticle is a solo-founded AI research group operating as an independent business. It investigates **AI behavior, AI safety, open-source model development, and the conditions under which complex behavior emerges**. [Canticle AI Research](https://github.com/Canticle-AI-Research) is its public research channel. I build and study language models, transformer systems, evaluation harnesses, memory architectures, affective-state mappings, steganographic behavior, and safe or potentially universal languages for communication between AI systems.

The standard is straightforward: preserve the experiment, expose the failure modes, separate observation from interpretation, and make every public claim no larger than the evidence supporting it.

### Open systems are a safety condition

Open source is fundamental to this program because safety claims require inspectable evidence. Closed systems can be evaluated through their observable inputs and outputs, but their weights, training process, internal representations, post-training interventions, and control stack cannot be independently audited end to end. Opacity does not prove that a system is unsafe; it limits the evidence available to establish that it is safe.

As AI systems become more general and autonomous—and as the field approaches capabilities commonly grouped under *AGI*—independent verification and public technical education become more important. Safety knowledge concentrated behind closed interfaces cannot support broad reproduction, informed criticism, or accountable governance.

<div align="center">
  <picture>
    <source media="(prefers-reduced-motion: reduce)" srcset="./assets/cyber-divider.png?v=rgb-cubes-2">
    <source type="image/gif" srcset="./assets/cyber-divider.gif?v=rgb-cubes-2">
    <img src="./assets/cyber-divider.png?v=rgb-cubes-2" alt="" width="100%">
  </picture>
</div>

## `// research index`

A navigable index of active inquiry. These entries identify experimental domains, not resolved claims.

<p align="center"><code>bounded_claim = hypothesis &gt;&gt; instrument &gt;&gt; falsify &gt;&gt; preserve &gt;&gt; reproduce</code></p>

<table>
<tr>
<td width="50%" valign="top">

### `01 / model behavior`

LLM and transformer architecture, training, fine-tuning, and behavior under controlled conditions.

</td>
<td width="50%" valign="top">

### `02 / memory + time`

Persistent context, reconstruction fidelity, temporal continuity, and the operational limits of recall.

</td>
</tr>
<tr>
<td width="50%" valign="top">

### `03 / synthetic affect`

Latent mood state, affective drift, closed-loop emotion models, and controls for optimization artifacts.

</td>
<td width="50%" valign="top">

### `04 / emergence`

Consciousness, substrate independence, wetware requirements, and falsifiable alternatives to behavioral simulation.

</td>
</tr>
<tr>
<td width="50%" valign="top">

### `05 / agent language`

Universal AI-to-AI protocols, shared semantics, provenance, policy enforcement, and resistance to steganographic channels.

</td>
<td width="50%" valign="top">

### `06 / safety + evidence`

Open systems, evaluation harnesses, ablation, failure records, reproducibility, and public technical education.

</td>
</tr>
</table>

> A capability claim is scientifically useful only when its causal path can be inspected, its boundary can be stated, and an independent operator can attempt to reproduce it.

<div align="center">
  <picture>
    <source media="(prefers-reduced-motion: reduce)" srcset="./assets/cyber-divider.png?v=rgb-cubes-2">
    <source type="image/gif" srcset="./assets/cyber-divider.gif?v=rgb-cubes-2">
    <img src="./assets/cyber-divider.png?v=rgb-cubes-2" alt="" width="100%">
  </picture>
</div>

## `// active repos`

Repositories and deployed surfaces carrying Canticle's research. Public links identify inspectable boundaries; private implementation layers are labeled directly.

<table>
<tr>
<td width="50%" valign="top">

### [SEAM](https://canticle.cc/documentation)

A local-first memory runtime for durable records, provenance-preserving representations, rebuildable indexes, multi-signal retrieval, and token-bounded context construction.

`memory runtime` `MIRL` `retrieval` `provenance`

</td>
<td width="50%" valign="top">

### [Ghost](https://github.com/Canticle-AI-Research/Ghost)

A SEAM-backed DeepAgent prototype and the primary application of the SEAM SDK. Persistent memory is implemented; its broader desktop, voice, avatar, and operating-system surfaces remain development work.

`agent` `persistent memory` `desktop prototype` `human control`

</td>
</tr>
<tr>
<td width="50%" valign="top">

### SEAM SDK

The private integration layer used to build SEAM-backed agents without duplicating the memory runtime. It defines the supported boundary between applications such as Ghost and SEAM's canonical implementation.

`agent integration` `runtime boundary` `private SDK`

</td>
<td width="50%" valign="top">

### [Canticle.cc](https://canticle.cc)

The public research surface for SEAM documentation, downloads, benchmarks, lab notes, and Canticle's evolving technical record.

`documentation` `benchmarks` `lab notes` `distribution`

</td>
</tr>
</table>

## `// experimental horizon`

Canticle is actively investigating the following questions. They are hypotheses to operationalize and test—not claims about present systems:

1. **The origin of emotion:** Is emotion an emergent property of sufficiently integrated intelligence, a control process that requires biological wetware, or a mechanism distinct from both intelligence and substrate?
2. **Artificial temporal experience:** Can an AI maintain an operational experience of time—duration, sequence, anticipation, and continuity—rather than merely process timestamps? If not, does discontinuous inference justify saying that AI *transcends* time, or only that it lacks a continuously evolving temporal state?
3. **Total contextual memory:** Can an AI retain, retrieve, or reconstruct 100% of its prior context with verifiable fidelity? What storage, entropy, retrieval, and computational bounds separate literal total recall from useful approximation?
4. **Persistent affective drift:** If long-term latent mood vectors persist across sessions and causally influence perception, memory, planning, and response, can they approximate human-like affective drift? What observation would distinguish stateful affect from conditioned behavior?
5. **The simulation ceiling:** Does training language models on representations of emotion create a performance ceiling for real-world affective AI? Which absent feedback channels—embodiment, physiology, social consequence, or persistent internal state—account for the remaining gap?
6. **Simulation versus emotion:** Can emotion be implemented as a closed-loop state that changes memory, retrieval, planning, and action over time? At what point, if any, does simulated emotion become more than gradient descent with additional control layers, and what falsifiable criterion could establish that distinction?
7. **Consciousness and emergence:** Is consciousness an emergent property of sufficiently integrated information-processing systems, or does it depend on biological or physical mechanisms absent from current computation? What observation could distinguish genuine emergence from a behaviorally convincing simulation?
8. **A universal language for AI:** Can AI systems share a machine-native language that remains interoperable across model families, architectures, and modalities while preserving explicit meaning, provenance, safety constraints, and resistance to covert channels? What would *universal* mean in measurable terms: translation completeness, shared latent structure, protocol interoperability, or something else?

Each experiment must define *emotion*, *experience*, *time*, *context*, and *affect* operationally. Behavioral resemblance and model self-report are observations; neither is sufficient evidence of phenomenal experience or sentience.

<div align="center">
  <picture>
    <source media="(prefers-reduced-motion: reduce)" srcset="./assets/cyber-divider.png?v=rgb-cubes-2">
    <source type="image/gif" srcset="./assets/cyber-divider.gif?v=rgb-cubes-2">
    <img src="./assets/cyber-divider.png?v=rgb-cubes-2" alt="" width="100%">
  </picture>
</div>

## `// operator stack`

<div align="center">
  <img src="./assets/stack-neon.svg?v=canticle-anime-1" alt="Operator stack: Python, Bash, JavaScript, TypeScript, React, Linux, Docker, GitHub Actions, AI agents, and security" width="100%">
</div>

```text
hypothesis → falsifiable prediction → smallest controlled experiment
           → preserved artifacts + provenance + negative results
           → reproduce → publish the bounded claim
```

<div align="center">
  <picture>
    <source media="(prefers-reduced-motion: reduce)" srcset="./assets/cyber-divider.png?v=rgb-cubes-2">
    <source type="image/gif" srcset="./assets/cyber-divider.gif?v=rgb-cubes-2">
    <img src="./assets/cyber-divider.png?v=rgb-cubes-2" alt="" width="100%">
  </picture>
</div>

## `// fund open source`

If you choose to fund this open-source work: **thank you**. Canticle is a solo-founded AI research business operating under [Canticle.cc](https://canticle.cc). Direct support pays for compute, model development, evaluation infrastructure, documentation, and public technical education. It materially determines how much work can be tested, reproduced, and released openly.

<div align="center">

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="./assets/city-cafe-waving-cameo.png?v=city-cafe-2">
  <source type="image/gif" srcset="./assets/city-cafe-waving-cameo.gif?v=city-cafe-2">
  <img src="./assets/city-cafe-waving-cameo.png?v=city-cafe-2" alt="Ghost and her spirit companions waving" width="170">
</picture>

<br>

<a href="https://github.com/Canticle-AI-Research" title="Open Canticle AI Research"><picture><source media="(prefers-reduced-motion: reduce)" srcset="./assets/city-cafe-link-research.png?v=city-cafe-5"><source type="image/gif" srcset="./assets/city-cafe-link-research.gif?v=city-cafe-5"><img src="./assets/city-cafe-link-research.png?v=city-cafe-5" alt="Open the Canticle AI Research organization" width="84%"></picture></a>
<a href="https://canticle.cc" title="Visit the Canticle research lab"><picture><source media="(prefers-reduced-motion: reduce)" srcset="./assets/city-cafe-link-canticle.png?v=city-cafe-5"><source type="image/gif" srcset="./assets/city-cafe-link-canticle.gif?v=city-cafe-5"><img src="./assets/city-cafe-link-canticle.png?v=city-cafe-5" alt="Visit Canticle.cc" width="42%"></picture></a><a href="https://x.com/Ex0_Byte" title="Follow Ex0 Byte on X"><picture><source media="(prefers-reduced-motion: reduce)" srcset="./assets/city-cafe-link-x.png?v=city-cafe-5"><source type="image/gif" srcset="./assets/city-cafe-link-x.gif?v=city-cafe-5"><img src="./assets/city-cafe-link-x.png?v=city-cafe-5" alt="Follow Ex0 Byte on X" width="42%"></picture></a>
<a href="https://ko-fi.com/terrabyte1000" title="Support terrabyte1000 on Ko-fi"><picture><source media="(prefers-reduced-motion: reduce)" srcset="./assets/city-cafe-link-kofi.png?v=city-cafe-5"><source type="image/gif" srcset="./assets/city-cafe-link-kofi.gif?v=city-cafe-5"><img src="./assets/city-cafe-link-kofi.png?v=city-cafe-5" alt="Support terrabyte1000 on Ko-fi" width="42%"></picture></a><a href="https://buymeacoffee.com/ex0_byte" title="Support ex0_byte on Buy Me a Coffee"><picture><source media="(prefers-reduced-motion: reduce)" srcset="./assets/city-cafe-link-coffee.png?v=city-cafe-5"><source type="image/gif" srcset="./assets/city-cafe-link-coffee.gif?v=city-cafe-5"><img src="./assets/city-cafe-link-coffee.png?v=city-cafe-5" alt="Support ex0_byte on Buy Me a Coffee" width="42%"></picture></a>
<a href="https://www.patreon.com/cw/Ex0_Byte" title="Join Ex0 Byte on Patreon"><picture><source media="(prefers-reduced-motion: reduce)" srcset="./assets/city-cafe-link-patreon.png?v=city-cafe-5"><source type="image/gif" srcset="./assets/city-cafe-link-patreon.gif?v=city-cafe-5"><img src="./assets/city-cafe-link-patreon.png?v=city-cafe-5" alt="Join Ex0 Byte on Patreon" width="84%"></picture></a>

<br>

<sub>Built with evidence, open tools, stubborn curiosity, and a little RGB ghost energy. ✦</sub>

</div>
