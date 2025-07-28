import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/xoptpy/blog',
    component: ComponentCreator('/xoptpy/blog', '93a'),
    exact: true
  },
  {
    path: '/xoptpy/blog/archive',
    component: ComponentCreator('/xoptpy/blog/archive', 'd7b'),
    exact: true
  },
  {
    path: '/xoptpy/blog/authors',
    component: ComponentCreator('/xoptpy/blog/authors', '11f'),
    exact: true
  },
  {
    path: '/xoptpy/blog/authors/all-sebastien-lorber-articles',
    component: ComponentCreator('/xoptpy/blog/authors/all-sebastien-lorber-articles', 'b21'),
    exact: true
  },
  {
    path: '/xoptpy/blog/authors/yangshun',
    component: ComponentCreator('/xoptpy/blog/authors/yangshun', 'bd6'),
    exact: true
  },
  {
    path: '/xoptpy/blog/first-blog-post',
    component: ComponentCreator('/xoptpy/blog/first-blog-post', '266'),
    exact: true
  },
  {
    path: '/xoptpy/blog/long-blog-post',
    component: ComponentCreator('/xoptpy/blog/long-blog-post', 'd5f'),
    exact: true
  },
  {
    path: '/xoptpy/blog/mdx-blog-post',
    component: ComponentCreator('/xoptpy/blog/mdx-blog-post', 'b06'),
    exact: true
  },
  {
    path: '/xoptpy/blog/tags',
    component: ComponentCreator('/xoptpy/blog/tags', '8fd'),
    exact: true
  },
  {
    path: '/xoptpy/blog/tags/docusaurus',
    component: ComponentCreator('/xoptpy/blog/tags/docusaurus', 'f54'),
    exact: true
  },
  {
    path: '/xoptpy/blog/tags/facebook',
    component: ComponentCreator('/xoptpy/blog/tags/facebook', '1a1'),
    exact: true
  },
  {
    path: '/xoptpy/blog/tags/hello',
    component: ComponentCreator('/xoptpy/blog/tags/hello', 'cf5'),
    exact: true
  },
  {
    path: '/xoptpy/blog/tags/hola',
    component: ComponentCreator('/xoptpy/blog/tags/hola', '43b'),
    exact: true
  },
  {
    path: '/xoptpy/blog/welcome',
    component: ComponentCreator('/xoptpy/blog/welcome', 'd78'),
    exact: true
  },
  {
    path: '/xoptpy/markdown-page',
    component: ComponentCreator('/xoptpy/markdown-page', '146'),
    exact: true
  },
  {
    path: '/xoptpy/docs',
    component: ComponentCreator('/xoptpy/docs', '60f'),
    routes: [
      {
        path: '/xoptpy/docs',
        component: ComponentCreator('/xoptpy/docs', '81e'),
        routes: [
          {
            path: '/xoptpy/docs',
            component: ComponentCreator('/xoptpy/docs', 'd78'),
            routes: [
              {
                path: '/xoptpy/docs/api/client',
                component: ComponentCreator('/xoptpy/docs/api/client', '67a'),
                exact: true,
                sidebar: "apiSidebar"
              },
              {
                path: '/xoptpy/docs/api/exceptions',
                component: ComponentCreator('/xoptpy/docs/api/exceptions', '49b'),
                exact: true,
                sidebar: "apiSidebar"
              },
              {
                path: '/xoptpy/docs/api/models',
                component: ComponentCreator('/xoptpy/docs/api/models', '932'),
                exact: true,
                sidebar: "apiSidebar"
              },
              {
                path: '/xoptpy/docs/api/overview',
                component: ComponentCreator('/xoptpy/docs/api/overview', '8c4'),
                exact: true,
                sidebar: "apiSidebar"
              },
              {
                path: '/xoptpy/docs/cli-usage',
                component: ComponentCreator('/xoptpy/docs/cli-usage', '23a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/xoptpy/docs/creating-modules',
                component: ComponentCreator('/xoptpy/docs/creating-modules', '8cf'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/xoptpy/docs/getting-started',
                component: ComponentCreator('/xoptpy/docs/getting-started', 'fda'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/xoptpy/docs/intro',
                component: ComponentCreator('/xoptpy/docs/intro', '33d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/xoptpy/docs/tutorial-basics/congratulations',
                component: ComponentCreator('/xoptpy/docs/tutorial-basics/congratulations', '0da'),
                exact: true
              },
              {
                path: '/xoptpy/docs/tutorial-basics/create-a-blog-post',
                component: ComponentCreator('/xoptpy/docs/tutorial-basics/create-a-blog-post', '6dd'),
                exact: true
              },
              {
                path: '/xoptpy/docs/tutorial-basics/create-a-document',
                component: ComponentCreator('/xoptpy/docs/tutorial-basics/create-a-document', '847'),
                exact: true
              },
              {
                path: '/xoptpy/docs/tutorial-basics/create-a-page',
                component: ComponentCreator('/xoptpy/docs/tutorial-basics/create-a-page', '418'),
                exact: true
              },
              {
                path: '/xoptpy/docs/tutorial-basics/deploy-your-site',
                component: ComponentCreator('/xoptpy/docs/tutorial-basics/deploy-your-site', '57b'),
                exact: true
              },
              {
                path: '/xoptpy/docs/tutorial-basics/markdown-features',
                component: ComponentCreator('/xoptpy/docs/tutorial-basics/markdown-features', '1a4'),
                exact: true
              },
              {
                path: '/xoptpy/docs/tutorial-extras/manage-docs-versions',
                component: ComponentCreator('/xoptpy/docs/tutorial-extras/manage-docs-versions', '687'),
                exact: true
              },
              {
                path: '/xoptpy/docs/tutorial-extras/translate-your-site',
                component: ComponentCreator('/xoptpy/docs/tutorial-extras/translate-your-site', 'ca6'),
                exact: true
              },
              {
                path: '/xoptpy/docs/working-with-tools',
                component: ComponentCreator('/xoptpy/docs/working-with-tools', 'd63'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/xoptpy/',
    component: ComponentCreator('/xoptpy/', '8dc'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
