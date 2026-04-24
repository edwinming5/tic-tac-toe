# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Git Workflow

After every change, commit with a clean descriptive message and push to GitHub so no work is ever lost.

## Running the App

Open `tictactoe.html` directly in a browser — no build step, no server required.

## Architecture

The entire app is a single self-contained file: `tictactoe.html`. It has three sections:

- **CSS** (lines 7–218): Theme variables via CSS custom properties on `:root[data-theme]`. All colors reference `var(--*)` tokens, so light/dark mode is a single attribute swap on `<html>`.
- **HTML** (lines 220–268): Static markup — theme toggle, scoreboard, 3×3 grid of `.cell` divs (identified by `data-index`), message area, and buttons.
- **JavaScript** (lines 269–374): Vanilla JS, no dependencies.
  - `board` (array[9]), `currentPlayer`, `gameOver` hold all game state.
  - `stats` (`{ X, O, draw }`) tracks session scores.
  - `WINS` is the static win-line lookup table.
  - Theme preference is persisted via `localStorage` key `ttt-theme`.
  - `startGame()` resets board state; "Reset Stats" zeroes `stats` then calls `startGame()`.
