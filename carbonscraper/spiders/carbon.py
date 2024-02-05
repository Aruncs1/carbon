# header files importing
import scrapy
import re

# a class is initiated to define the spider and spider is imported
class CarbonSpider(scrapy.Spider):
    name = 'carbon'
    allowed_domains = ["carbon38.com"]
    start_urls = ["https://www.carbon38.com/shop-all-activewear/tops"]
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    # function for parsing the front page elements

    def parse(self, response):
        for product in response.css("div.ProductItem__Wrapper"):
            product_name = product.css('h2.ProductItem__Title.Heading a::text').extract_first()
            brand = product.css('h3.ProductItem__Designer::text').extract_first()
            price = product.css('span.ProductItem__Price.Price::text').extract_first()
            image = product.css('img::attr(src)').extract_first()

            
            product_link = product.css('h2.ProductItem__Title.Heading a::attr(href)').extract_first()
            yield scrapy.Request(url=response.urljoin(product_link), callback=self.parse_product_details,
                                 meta={'brand': brand, 'price': price, 'product_name': product_name, 'image': image})

        # to crawl from the first page to last one pagination is done by checking the existance of next page and code for crawling to next
        next_page = response.css('div.Pagination__Nav a[title="Next page"]::attr(href)').extract_first()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)
    # To  parse from the inside of the field it is directed to the inside of the item 
    def parse_product_details(self, response):
        brand = response.meta['brand']
        price = response.meta['price']
        product_name = response.meta['product_name']
        image = response.meta['image']

        # Extract SKU, selected color,sizes,product id,description
        sku = response.css('select[name="id"] option::attr(data-sku)').get()
        selected_color = response.css('.ProductForm__SelectedValue::text').get()
        sizes = set(response.css('.SizeSwatchList input[type="radio"]::attr(value)').getall())
        product_id = response.css('div.yotpo-widget-instance::attr(data-yotpo-product-id)').get()
        # review_text = response.css('.yotpo-sr-bottom-line-text--right-panel::text').get()
        # num_reviews = re.search(r'\d+', review_text).group() if review_text else None
        editors_notes = response.css('.Faq__ItemWrapper button.Faq__Question:contains("Editor\'s Notes") + .Faq__AnswerWrapper .Faq__Answer.Rte span::text').getall()
        editors_notes = ' '.join(map(str.strip, editors_notes))

        # Yield the combined information that got frome previously
        yield {
            'Image_url': image,
            'Brand': brand,
            'Product Name': product_name,
            'Price': price,
            # 'Reviews': num_reviews,
            'Color': selected_color,
            'Sizes': list(sizes),
            'Descriptions': editors_notes,
            'SKU': sku,
            'Product_ID': product_id,
            
        }
