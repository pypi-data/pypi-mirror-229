"""# HtPy5\n
| is a module made to make the website making more better with python,that is an experiment version
\n
Here is a simple example :\n
```python
from HTPy5 import WeBBuild
from HTPy5.Webgets import Widgets
    
builder = WeBBuild()
builder.setup(title="My Page",
              lang="en",
              description="That is my webpage")
    
builder.addLinking(LinkFileName="style.css", LinkType="stylesheet")
builder.addLinking(LinkFileName="responsive.css", LinkType="stylesheet")
builder.addLinking(LinkFileName="print.css", LinkType="stylesheet")
    
builder.addMeta("author", "BoodyWin Workshop")
builder.addMeta("keywords", "python, web development, meta tags")
    
builder.addNewBodyElement(Widgets.button("that is a button"))
    
if __name__ == "__main__":
    html = builder.generateHTML()
    with open("index.html","w") as f:
        f.write(html)
    
```
Copyright(c) by BoodyWin Workshop


Note : Some notes is AI generated.
"""
#                                                                        
#   ███      ███  █████████████████  ██████████     ███          ███     ███████████   
#   ███      ███         ███         ███      ███     ███       ███      ███           
#   ███      ███         ███         ███      ███      ███     ███       ███           
#   ███      ███         ███         ███      ███       ███   ███        ███           
#   ████████████         ███         ██████████           ██ ██          ██████████     
#   ███      ███         ███         ███                   ███                     ███
#   ███      ███         ███         ███                   ███                     ███
#   ███      ███         ███         ███                   ███                     ███
#   ███      ███         ███         ███                   ███           ██████████     
#                                                                                                                                                                                                                       
#                                                                                                                                           
#                                    ██      ██   ████           █████          █████  
#                                    ██      ██     ██          ██   ██        ██   ██ 
#                                     ███  ███      ██          ██   ██        ██   ██ 
#                                       ████        ██          ██   ██        ██   ██
#                                        ██       ██████   ██    █████    ██    █████    
#                                                                                                                                       
class SetupError(Exception):
    def __init__(self, message="Cannot generate the HTML without setting up the webpage (or calling `setup()` in the main code)."):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class WeBBuild:
    def __init__(self):
        self.setuped = False
        self.title = ""
        self.lang = ""
        self.description = ""
        self.links = []
        self.charset = "<meta charset=\"UTF-8\">"
        self.viewport = "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">"
        self.meta_tags = []
        self.elements = []
        self.head_elements = []

    def setup(self, title="Document", lang="en", viewport=None, charset="UTF-8", description=None):
        self.lang = lang
        self.charset = f"<meta charset=\"{charset}\">"
        self.title = f"<title>{title}</title>"
        if viewport:
            self.viewport = f"<meta name=\"viewport\" content=\"{viewport}\">"
            
        if description:
            self.description = f"<meta name=\"description\" content=\"{description}\">"
        self.setuped = True
        
        

    def addLinking(self, LinkFileName: str, LinkType: str = "stylesheet"):
        """The `addLinking()` method is used to add a link to the webpage.

        Args:
            LinkFileName (str): The href of the link.
            LinkType (str, optional): The type of the link. Defaults to "stylesheet".

        Returns:
            str: The tag of the link.
        """
        link_tag = f"<link rel=\"{LinkType}\" href=\"{LinkFileName}\">"
        self.links.append(link_tag)
        
        return link_tag


    def addMeta(self, MeName: str, MeContent: str):
        """The `addMeta()` method is used to add a meta tag to the webpage.

        Args:
            MeName (str): The name of the meta tag.
            MeContent (str): The content of the meta tag.

        Returns:
            str: The tag of the meta.
        """
        meta_tag = f"<meta name=\"{MeName}\" content=\"{MeContent}\">"
        self.meta_tags.append(meta_tag)
        
        return meta_tag
        
    def addCustomMeta(self,**attributes):
        """The `addCustomMeta()` method is used to add a custom meta tag to the webpage.

        Returns:
            str: The custom meta.
        """
        meta_attr = " ".join([f"{attr}='{val}'" for attr, val in attributes.items()])
        self.meta_tags.append(f"<meta {meta_attr}>")
        
        return f"<meta {meta_attr}>"
        
    def addNewHeadElement(self,Widget):
        """The `addNewHeadElement()` method is used to add a new element to the head of the webpage.

        Args:
            Widget (Webgets): The widget from webgets.

        Returns:
            str: The widget tag.
        """
        self.head_elements.append(Widget)
        return Widget

    def addNewBodyElement(self,Widget):
        """The `addNewBodyElement()` method is used to add a new element to the body of the webpage.

        Args:
            Widget (Webgets): The widget from webgets.

        Returns:
            str: The widget tag.
        """
        self.elements.append(Widget)
        return Widget
    
    def generateHTML(self):
        if self.setuped:
            all_meta_tags = "\n    ".join(self.meta_tags)
            all_css_links = "\n    ".join(self.links)
            all_elements = "\n    ".join(self.elements)
            all_head_elements = "\n    ".join(self.head_elements)
            lang_attr = f" lang=\"{self.lang}\"" if self.lang else ""
            html = f"""<!DOCTYPE html>
<html{lang_attr}>
<head>
    {self.title}
    {self.description}
    {self.charset}
    {self.viewport}
    {all_meta_tags}
    {all_head_elements}
    {all_css_links}
</head>
<body>
    {all_elements}
</body>
</html>"""
            return html
        else:
            raise SetupError("Cannot generate the HTML without setting up the webpage (or calling `setup()` in the main code).")

__all__ = ['Webgets','WeBuild']
__version__ = "1.0.0"

# Example usage:
def main():
    from flask import Flask
    from Webgets import Widgets

    app = Flask(__name__)

    builder = WeBBuild()
    builder.setup(title="My Page",
                lang="en",
                description="This is my HTPy5 webpage",
                viewport="width=device-width, initial-scale=1.0",
                charset="UTF-8")

    builder.addLinking(LinkFileName="style.css", LinkType="stylesheet")
    builder.addMeta("author", "BoodyWin Workshop")
    builder.addMeta("keywords", "python, web development, meta tags, HTPy5")
    builder.addNewBodyElement(Widgets.button("This is a button"))
    builder.addNewBodyElement(Widgets.button(value="That is a styled button",ID="styled-button",style="background-color: Blue;border:2px solid black;border-radius:1em;color:white;padding: 8px;"))

    @app.route("/")
    def index():
        return builder.generateHTML()
    
    import webbrowser
    webbrowser.open(url="http://127.0.0.1:3000/")
    app.run(debug=True, port=3000)

if __name__ == "__main__":
    main()