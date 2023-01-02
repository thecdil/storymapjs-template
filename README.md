# storymapjs-template

**This is a work in progress! This template is not finished!**

[storymapjs-template](https://github.com/evanwill/storymapjs-template) is a basic Jekyll template for creating self-hosted [StoryMapJS](https://storymap.knightlab.com/) on GitHub Pages (or where ever you want to host it!). 

It is compatible with existing projects created using the StoryMapsJS authoring tool or standard StoryMapsJS formatted JSON files.
Additionally, storymapjs-template supports a spreadsheet template that simplifies manually creating your storymap data.

See [docs/storymap.md](docs/storymap.md) to get started!

Demo: <https://thecdil.github.io/storymapjs-template>

*Note:* since the template implements self hosted StoryMapJS, please explore [StoryMapJS advanced](https://storymap.knightlab.com/advanced/) for more examples, data format documentation, and advanced features.

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

The basic steps to using storymapjs-template are: 

1. create repository from the template (click the green "Use this template" button to make a copy of the code in your own repository)
2. add storymap data (to the "storymaps" folder as either JSON or CSV)
3. add storymap to a page

Check [docs/storymap.md](docs/storymap.md) for the full details. 

## Customize 

This template is based on [bootstrap5-template](https://github.com/thecdil/bootstrap-template), so you can use [Bootstrap 5](https://getbootstrap.com/) and the built in features to tweak the theme:

- Edit "_config.yml" with your site information to populate header and footer
- Use "includes" to simplify adding Bootstrap features to Markdown pages (see comments in the "_include/" files for instructions)
- Tweak base variables in `assets/css/main.scss` (text color, link color, container size)
- Tweak bootstrap theme colors using `_data/theme-colors.csv` (add a css color in the color column next to the BS color-class to override, or create a new class name. This will generate btn-, text-, and bg- classes.)
- Add custom CSS to `_sass/_custom.scss` (content of `_sass/_template.scss` relates to template components)
- Use Bootstrap to customize `_layouts/` and `_includes/template/`.

See [docs/create-website.md](https://github.com/thecdil/storymapjs-template/blob/main/docs/create-website.md) for more details.

## Template Assets

Included in assets/lib folder:

- [Bootstrap](https://getbootstrap.com/docs/5.1/getting-started/introduction/) 5.1
- [Bootstrap Icons](https://icons.getbootstrap.com/) 1.7.1
- [lunr.js](https://lunrjs.com/) 2.3.9
- [lazysizes](https://github.com/aFarkas/lazysizes) 5.3.2
- [StoryMapJS](https://github.com/NUKnightLab/StoryMapJS/) 0.7.7
- [Papa Parse](https://www.papaparse.com/) 5.0 
