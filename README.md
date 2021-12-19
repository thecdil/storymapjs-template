# storymapjs-template

[storymapjs-template]() is a basic Jekyll template for creating self-hosted [StoryMapJS](https://storymap.knightlab.com/) on GitHub Pages (or where ever you want to host it!). 

It is compatible with existing projects created in Google Sheets following the StoryMapsJS template or can be used with StoryMapsJS formatted JSON files.

See [docs/storymap.md]() to get started!

Demo: 

*Note:* since the template implements self hosted StoryMapJS, please explore [StoryMapJS advanced](https://storymap.knightlab.com/advanced/) for more examples, data format documentation, and advanced features.

## Why storymapjs-template?

[StoryMapJS](https://storymap.knightlab.com/) is a very popular open-source project to create visual map based stories that can be embedded on a webpage.
Their "authoring tool" provides an easy way to create and publish a storymap embed using Google Sheets.
This is great for getting started with minimal setup and no overhead.

However, relying on Google Sheets can be problematic:

- API outages and changes unexpectedly break the StoryMapJS service and make in unsustainable in the long term
- you may not have a convenient location to host your media files or a website to embed your timelines
- Google platform exposes your users to unnecessary privacy tradeoffs

To avoid these issues you can [self-host your StoryMapJS projects](https://storymap.knightlab.com/advanced/) and use the [standalone javascript](https://github.com/NUKnightLab/StoryMapJS/) to create your story map without relying on any 3rd party services.

The `storymapjs-template` implements the basics of StoryMapJS in a simple Jekyll project template to make self-hosting easy on [GitHub Pages](https://pages.github.com/).
This approach is more sustainable, keeping the library assets, metadata, and media together in a self-contained package (rather than multiple 3rd party platforms).

## Get Started 

- Click green "Use this template" button to make a copy of the code in your own repository (alternatively, use Import or manually copy files)
- Edit `_config.yml` with your site information
- In your new repository visit "Settings" > "Pages" to activate GitHub Pages
- Edit and create pages in the "pages" folder (probably in Markdown). Use each page's yaml front matter to populate the navbar:
    - `title` will appear as h1 at top of the page content.
    - `nav` if this option has a value, it will appear in the navbar as link to this page.
    - `nav_order` navbar items will be sorted using this number. 
- Use "includes" to simplify adding Bootstrap features to Markdown pages (see comments in the "_include/" files for instructions).

See [docs/create-website.md](https://github.com/thecdil/bootstrap5-template/blob/main/docs/create-website.md) for more details.

## Customize 

- Tweak base variables in `assets/css/custom.scss` (text color, link color, container size)
- Tweak bootstrap theme colors using `_data/theme-colors.csv` (add a css color in the color column next to the BS color-class to override, or create a new class name. This will generate btn-, text-, and bg- classes.)
- Add custom CSS to `_sass/_custom.scss` (content of `_sass/_template.scss` relates to template components)
- Use Bootstrap to customize `_layouts/` and `_includes/template/`.

## Template Assets

storymapjs-template is built on [bootstrap5-template](https://github.com/thecdil/bootstrap-template)--a basic template repository to create a [Bootstrap 5](https://getbootstrap.com/) site using Jekyll on GitHub Pages (or where every you want to host it). 

Included in assets/lib folder:

- [Bootstrap](https://getbootstrap.com/docs/5.1/getting-started/introduction/) 5.1
- [Bootstrap Icons](https://icons.getbootstrap.com/) 1.7.1
- [lunr.js](https://lunrjs.com/) 2.3.9
- [lazysizes](https://github.com/aFarkas/lazysizes) 5.3.2
- [StoryMapJS](https://storymap.knightlab.com/advanced/)
