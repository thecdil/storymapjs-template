# Using storymapjs-template

The basic steps to using storymapjs-template are: 

1. create repository from the template
2. add storymap data
3. add storymap to a page

There are two builtin options for adding StoryMapJS timelines to the pages of your site: Basic Timeline (using a spreadsheet) or JSON Timeline (using JSON file). 
How the timeline is embedded in the page can be controlled using the `layout` value.
These options are described below.
See docs/customize.md for builtin options to customize the website nav and look. 

## 1. Set up repository

- Visit storymapjs-template: <https://github.com/thecdil/storymapjs-template>
- Make your own copy of the repository by clicking the green "Use this template" button (alternatively, use Import or manually copy files to a new repo).
- Edit `_config.yml` with your site information.
    - `title` will appear in the navbar with link to home page.
    - `year` and `author` appear in footer.
    - site urls (`url` and `baseurl`) are optional if using GitHub Pages, but should be filed in if hosting else where.
- Activate GitHub Pages. 
    - On your repository visit "Settings", click on the "Pages" option on the left side nav, select Branch "main" from the drop down, and click Save. 
    - Once activated, it will provide your new URL, following the pattern `https://username.github.io/repository_name`

## 2. Set up StoryMapJS Data

### Export Your Existing StoryMapJS JSON File

If you create a StoryMapJS using the "authoring tool" there is no immediate way to export your project's data.
To get the JSON:

1. Save any changes and publish your project. 
2. Click the "Share" button.
3. Copy the link at the top of the Share modal. The link will look something like:
   `https://uploads.knightlab.com/storymapjs/2492477e70c5d1f0ed169862b41f9707/example-project/index.html`
4. Paste the link into your browser address bar, but replace the "index.html" with "published.json". The link will look something like: 
   `https://uploads.knightlab.com/storymapjs/2492477e70c5d1f0ed169862b41f9707/example-project/published.json`
5. Save the resulting JSON file with a descriptive name (use a web safe filename with out spaces or special characters!).
6. Put your JSON file in your storymapjs-template project inside the "storymaps" folder.

## 3. Add to a Page

### Layout options

The page `layout` set in the front matter controls how the storymap will be displayed in the template.
These options are available:

- `storymap-page` timeline will be inside a container, with navbar, title in h1, and any content above.
- `storymap-full` timeline will be inside a container-fluid, with navbar, title in h1, and any content above.
- `default` timeline will be 100% width with no x margins, with navbar above.
- `storymap-embed` timeline will be the only content inside html element, so that it can be used as src in an iframe embed on another site.

Content can be written on the page and will appear above the timeline. 
If the `timeline` option is not added to the front matter, the stub will act as a normal content page.
