.. _crosslinker-documentation:

CrossLinker Documentation
=========================

Description
-----------

CrossLinker is a Python library designed for intelligently linking specific keywords within HTML text content. It enhances SEO (Search Engine Optimization) strategies by optimizing content with linked keywords, maintaining readability, and preventing over-optimization.

Table of Contents
-----------------

1. `Installation <#installation>`_
2. `How It Works <#how-it-works>`_
    - `Initialization <#initialization>`_
    - `Text Processing <#text-processing>`_
    - `Randomization (Optional) <#randomization-optional>`_
    - `Benefits for SEO <#benefits-for-seo>`_
3. `Usage <#usage>`_
    - `Example <#example>`_
    - `Parameters <#parameters>`_
    - `Result <#result>`_

Installation
------------

To install CrossLinker, you can use pip:

.. code-block:: bash

    pip install crosslinker

Text Processing
---------------

The library processes the HTML text and replaces keywords with links. This process includes tokenization, keyword matching, link insertion, HTML escaping, punctuation handling, and link limitation.

Randomization (Optional)
------------------------

You can choose to place links randomly (if ``random_links`` is set to True), which can help avoid over-optimization penalties from search engines.

Initialization
--------------

To get started, create an instance of the CrossLinker class by providing the following parameters:

- ``html_text``: The HTML text content you want to process. (Required)
- ``keywords``: A list of keyword-link pairs where each item is a list with the keyword and its associated link. (Required)
- ``density``: The maximum allowed length (in characters) for linked text snippets. (Default: 500)
- ``random_links``: If set to True, the library will randomly choose keywords to link each time. If False, it will consistently link the same keywords. (Default: False)
- ``stemming``: If set to True, keywords are stemmed before processing. (Default: True)
- ``language``: The language to use for stemming. Supported languages include "arabic," "danish," "dutch," "english," "finnish," "french," "german," "hungarian," "italian," "norwegian," "porter," "portuguese," "romanian," "russian," "spanish," and "swedish." (Default: "english")
- ``valid_tags``: A list of HTML tags that are considered valid for keyword linking. (Default: ["p", "h1", "h2", "h3", "h4", "h5", "h6"])

Benefits for SEO
----------------

CrossLinker offers several benefits for SEO:

- **Keyword Linking:** It automatically identifies and links keywords to relevant URLs within your HTML content, improving search engine understanding and rankings.
- **Content Optimization:** By strategically linking keywords, you can enhance the SEO value of your content and increase its visibility in search results.
- **Prevents Over-Optimization:** The library limits the number of linked keywords to maintain a natural keyword density, helping you avoid SEO penalties.
- **Maintains Readability:** Linked keywords are embedded within readable text snippets, improving the user experience and preventing content from appearing spammy.

Usage
-----

Here's an example of how to use the CrossLinker library:

Example
-------

.. code-block:: python

    from crosslinker import CrossLinker

    html_text = """
    <h1>Enhance Your SEO with CrossLinker</h1>
    <p>CrossLinker is a powerful Python library that can help boost your website's SEO performance. By intelligently linking specific keywords within your content, you can improve search engine rankings and increase organic traffic.</p>
    <p>Here are some examples of keywords you can link:</p>
    <ul>
        <li>Search Engine Optimization</li>
        <li>Keyword Research</li>
        <li>On-Page SEO</li>
        <li>Link Building</li>
    </ul>
    """

    keywords = [
        [["Search Engine Optimization"], "https://example.com/seo"],
        [["Keyword Research"], "https://example.com/keyword-research"],
        [["On-Page SEO"], "https://example.com/on-page-seo"],
        [["Link Building"], "https://example.com/link-building"],
        # Add more keyword-link pairs as needed
    ]

    # Initialize CrossLinker
    seo_html = CrossLinker(
        html_text=html_text,
        keywords=keywords,
        density=100,
        random_links=False,
        stemming=True,
        language="english",
        valid_tags=["li", "p", "h1", "h2", "h3", "h4", "h5", "h6"],
    )

    # Generate the processed HTML content
    processed_html = seo_html.make()

    print(processed_html)

Result
------

The ``processed_html`` variable will contain the HTML content with keywords replaced by links. This processed content can be used to enhance SEO strategies.

Thank you!
-----------

Please feel free to reach out if you have any further questions or need additional assistance!
