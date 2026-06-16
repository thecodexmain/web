import http.server
import socketserver
import re
import urllib.parse

PORT = 8000

class CustomRouter(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = parsed_url.query
        
        # Route: /product-details/:id -> /product_details.html?id=:id
        if path.startswith('/product-details/'):
            m = re.match(r'^/product-details/(\d+)', path)
            if m:
                prod_id = m.group(1)
                new_query = f"id={prod_id}"
                if query:
                    new_query += f"&{query}"
                self.path = f"/product_details.html?{new_query}"
                print(f"[Route] Redirected {path} to {self.path}")
                
        # Route: /payment/:prices -> /payment.html?prices=:prices
        elif path.startswith('/payment/'):
            m = re.match(r'^/payment/([\d\.]+)', path)
            if m:
                prices = m.group(1)
                new_query = f"prices={prices}"
                if query:
                    new_query += f"&{query}"
                self.path = f"/payment.html?{new_query}"
                print(f"[Route] Redirected {path} to {self.path}")
                
        # Route: /address -> /address.html
        elif path == '/address' or path == '/address/':
            new_query = query
            self.path = f"/address.html"
            if new_query:
                self.path += f"?{new_query}"
            print(f"[Route] Redirected {path} to {self.path}")
            
        # Route: /ordersummdary -> /ordersummdary.html
        elif path == '/ordersummdary' or path == '/ordersummdary/':
            new_query = query
            self.path = f"/ordersummdary.html"
            if new_query:
                self.path += f"?{new_query}"
            print(f"[Route] Redirected {path} to {self.path}")
            
        # Route: /admin -> /admin.html
        elif path == '/admin' or path == '/admin/':
            new_query = query
            self.path = f"/admin.html"
            if new_query:
                self.path += f"?{new_query}"
            print(f"[Route] Redirected {path} to {self.path}")
            
        # API Route: GET /api/config -> Return config.json
        if path == '/api/config':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(b'{"upi_id": "merchant@ybl"}')
            return

        # API Route: GET /api/orders -> Return orders.json
        elif path == '/api/orders':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            if os.path.exists('orders.json'):
                with open('orders.json', 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(b'[]')
            return

        return super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        # Helper to read request body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''
        
        # Endpoint: POST /save-products -> Save evaluated products array
        if path == '/save-products':
            try:
                products_list = json.loads(post_data.decode('utf-8'))
                with open('products.json', 'w', encoding='utf-8') as f:
                    json.dump(products_list, f, indent=2, ensure_ascii=False)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "success", "message": "products.json saved"}')
                print("[API] Saved products.json successfully")
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(f'{{"status": "error", "message": "{str(e)}"}}'.encode('utf-8'))
                print(f"[API] Error saving products: {e}")
            return
            
        # Endpoint: POST /log -> Save client log for debugging
        elif path == '/log':
            try:
                log_text = post_data.decode('utf-8')
                with open('client_logs.txt', 'a', encoding='utf-8') as f:
                    f.write(log_text + '\n')
                self.send_response(200)
                self.end_headers()
            except Exception as e:
                self.send_response(400)
                self.end_headers()
            return

        # Endpoint: POST /api/config -> Update UPI ID
        elif path == '/api/config':
            try:
                config_data = json.loads(post_data.decode('utf-8'))
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "success", "message": "config.json updated"}')
                print("[API] Updated config.json successfully")
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(f'{{"status": "error", "message": "{str(e)}"}}'.encode('utf-8'))
            return

        # Endpoint: POST /api/orders -> Append or overwrite orders
        elif path == '/api/orders':
            try:
                payload = json.loads(post_data.decode('utf-8'))
                
                orders = []
                if isinstance(payload, list):
                    # Overwrite/Clear list
                    orders = payload
                else:
                    # Append single order
                    if os.path.exists('orders.json'):
                        try:
                            with open('orders.json', 'r', encoding='utf-8') as f:
                                orders = json.loads(f.read())
                        except:
                            pass
                    orders.append(payload)
                
                with open('orders.json', 'w', encoding='utf-8') as f:
                    json.dump(orders, f, indent=2, ensure_ascii=False)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "success", "message": "orders updated"}')
                print("[API] Orders list updated successfully")
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(f'{{"status": "error", "message": "{str(e)}"}}'.encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

import os
import json

if __name__ == '__main__':
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), CustomRouter) as httpd:
        print(f"Server running at http://localhost:{PORT}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()
