from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import dns.resolver
import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_ip_address(domain):
    try:
        result = dns.resolver.resolve(domain, 'A')
        return [ipval.to_text() for ipval in result]
    except dns.resolver.NoAnswer:
        return ["No IP address found"]
    except Exception as e:
        return [f"Error: {str(e)}"]


def get_mx_records(domain):
    try:
        result = dns.resolver.resolve(domain, 'MX')
        return [exchange.exchange.to_text() for exchange in result]
    except dns.resolver.NoAnswer:
        return ["No MX records found"]
    except dns.resolver.NXDOMAIN:
        return ["Domain does not exist"]
    except Exception as e:
        return [f"Error: {str(e)}"]


@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/check", response_class=HTMLResponse)
async def check_link(request: Request, url: str = Form(...)):
    # Extract the domain and remove 'www' if present
    domain = url.replace('http://', '').replace('https://', '').split('/')[0]
    if domain.startswith("www."):
        domain = domain[4:]
    
    ip_addresses = get_ip_address(domain)
    mx_records = get_mx_records(domain)
    current_time = datetime.datetime.now().strftime("%b-%d-%Y")
    return templates.TemplateResponse(
        "index.html", {
            "request": request,
            "url": url,
            "ip_addresses": ip_addresses,
            "mx_records": mx_records,
            "current_time": current_time
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
