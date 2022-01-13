---
title: About This Template
nav: About
nav_order: 2
layout: page-narrow
---

**This is a work in progress! This template is not finished!**

[storymapjs-template](https://github.com/evanwill/storymapjs-template) is a basic Jekyll template for creating self-hosted [StoryMapJS](https://storymap.knightlab.com/) on GitHub Pages (or where ever you want to host it!). 

It is compatible with existing projects created using the StoryMapsJS authoring tool or standard StoryMapsJS formatted JSON files.
Additionally, storymapjs-template supports a spreadsheet template that simplifies manually creating your storymap data.

## Why storymapjs-template?

[StoryMapJS](https://storymap.knightlab.com/) from Northwestern University's Knight Lab is a popular open-source project to create visual map based stories that can be embedded on a webpage.
Their "authoring tool" provides a method to create and publish a storymap embed using your Google account.
This is great for getting started with minimal setup and no overhead.

However, relying on this platform can be problematic:

- API outages and changes unexpectedly break the StoryMapJS service and make it unsustainable in the long term.
- you may not have a convenient location to host your media files or a website to embed your timelines.
- if you already have structured data, using the "authoring tool" is a big pain... It might be easier to use a spreadsheet or create your own JSON.

To avoid these issues you can [self-host your StoryMapJS projects](https://storymap.knightlab.com/advanced/) and use the [standalone javascript](https://github.com/NUKnightLab/StoryMapJS/) to create your story map without relying on any 3rd party services.

The `storymapjs-template` implements the basics of StoryMapJS in a simple Jekyll project template to make self-hosting easy on [GitHub Pages](https://pages.github.com/).
This approach is more sustainable, keeping the library assets, metadata, and media together in a self-contained package (rather than multiple 3rd party platforms).

## Get Started 

The basic steps for using storymapjs-template are: 

1. Create repository from the template
2. Edit "_config.yml"
3. Add your StoryMap data
4. Add to a page and edit content
5. Use builtin customization options
6. Active GitHub Pages

See [docs/storymap.md](docs/storymap.md) for details!
