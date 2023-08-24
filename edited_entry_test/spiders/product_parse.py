import json
import scrapy
from edited_entry_test.items import ProductItem


class ParseProductSpider(scrapy.Spider):
    name = "product_parse"
    allowed_domains = ["shop.mango.com"]
    start_urls = ["https://shop.mango.com/gb/women/skirts-midi/midi-satin-skirt_17042020.html?c=99"]
    # all the product data is stored in a json file on the following url, ending with the product id
    json_file_url = "https://shop.mango.com/services/garments/006/en/S/"
    custom_settings = {
        'ITEM_PIPELINES': {
            # Store the parsed data in products.json
            "edited_entry_test.pipelines.JsonWithEncodingPipeline": 300,
        }
    }

    def parse(self, response):
        # Extract the product id from the response url and attach it to the json file url.
        # This code is placed here, since we scrape the product directly. Otherwise, it would be in parse_product()
        product_id = self.get_product_id(response.url)
        self.json_file_url += product_id

        yield scrapy.Request(self.json_file_url, callback=self.parse_product)

    @staticmethod
    def parse_product(response):
        json_data = json.loads(response.text)
        item = ProductItem()
        # Extract the information about the default color. The data about the price and the size are inside
        default_colour = [colour for colour in json_data["colors"]["colors"] if "default" in colour][0]

        item["name"] = json_data["name"]
        item["colour"] = default_colour["label"]
        item["price"] = default_colour["price"]["price"]
        item["size"] = [size["label"] for size in default_colour["sizes"]]

        yield item

    @staticmethod
    def get_product_id(prod_id):
        # Extracts the product id from the parsed url
        id_start_index = prod_id.rfind('_') + 1
        id_end_index = prod_id.index('.html')
        return prod_id[id_start_index:id_end_index]
