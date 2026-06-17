---
name: draft-a-readme
description: This skill can be triggered through the slash command call `/draft-a-readme`. This skill writes a README file from scratch in the root directory of a project.
---

# About This Skill

This skill is designed to draft a decent one-shotted sample README that can be proofread and published fast. READMEs shouldn't be one-shotted, so it's recommended to use this skill as a starting point and then iterate on it with human feedback. The README should be concise, bulleted, and to the point, but also easy to understand and follow, even for someone who is new to the project.

# Instructions

- Without prompting, write a README to the root directory of a project.
- Follow the workflow below alongside structural instructions.

# Workflow

1. Get current `README.md` state, and compare to decide whether to overwrite it or not.
  - If the README is empty, near-empty, or doesn't exist, then overwrite it.
  - If the README is lengthy, prompt user to view it and decide whether to overwrite it or not.
    - If user decides to overwrite it, then overwrite it.
    - If user decides not to overwrite it, then stop the workflow and do nothing.
2. Read all files in the current local repository to understand the project and its context.
3. Write a README file from scratch in the root directory of the project following the structural and general instructions for construction.

# README Structure

- Past the header, separate each section only with "`<br>`" for better readability.

## Main Header

- It should be aligned center.
- It should include the following:
  - Project Title
  - Description (one or two sentences describing the project and its purpose)
  - Badges (ordered: language version coverage, listed requirement libraries, license, and build status; from `https://img.shields.io/badge` with style (e.g., `![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)`))
  - "`---`" to separate the main header from the rest of the README

## Sections

- The rest of the sections should be ordered and titled as follows, with the corresponding content under each section:
  - "Ⅰ • Table of Contents"
  - "Ⅱ • Features"
  - "Ⅲ • Demonstration"
  - "Ⅳ • Quick Start"
  - "Ⅴ • Installation"
  - "Ⅵ • Usage"
  - "Ⅶ • Configuration"
  - "Ⅷ • Reference"
  - "Ⅸ • License"
  - "Ⅹ • Authors"
  - "Ⅺ • Contact"

## Footer

- "`---`"
- "*Last Updated: `<current date>`*" (e.g., "*Last Updated: June 1, 2024*")