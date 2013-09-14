# IdentiChip

After I wrote the Microchip Website I saw that most the Microchip world is very fragmented. To Search for a Microchip you have to got to all the Providers and type in the Chip Number. So I thought why not build a central point for this all to happen.

I'm currently writing this and hope to have code soon. It's basicly a Google for Microchip Providers. A Users types in a Microchip number and I search all the providers that registered and implemented my API for the chip. One Stop Search for all Microchips. I'm also giving Assocations that need this information the change to register and access the info from the providers giving users and breed associations access to a one stop site to manage all their information.

Microchip Providers Integrate with the system by opening up a certain url that will expose the data to the server for a search.

## Presentations

Going to be doing a presentation on the Site on the 27th of October in Cape Town. Any interested feel free to join.

## Running

Running the system is not quite that difficult.

All you need is the source and Google App Engine Local Dev Server.

Checkout a Copy of our Source and then run the Directory in the Local App Engine Server:

	$ dev_appserver.py IdentiChip/

Visit localhost:8080 and you should be ready to go. Note the port can differ on diffrent platforms. That's just the default on OSX.

## API

The service offers a API that the user can use to search for microchips.

View the Documentation for the API at http://www.identichip.org/developer

## Contributors

* Johann du Toit

## License

(MIT License)

Copyright (c) 2012 Johann du Toit

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
