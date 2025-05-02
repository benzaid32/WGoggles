import { NextResponse } from 'next/server';
import https from 'node:https';
import { Readable } from 'node:stream';
import { Buffer } from 'node:buffer';

// Configure API to not use Edge runtime
export const runtime = 'nodejs';

export async function POST(request: Request) {
  try {
    // Get form data from the incoming request
    const formData = await request.formData();
    console.log('Received form data, forwarding to recognition service...');
    
    // We need to create a custom fetch function using Node.js https module
    // to handle self-signed certificates
    const response = await new Promise<any>((resolve, reject) => {
      // Convert FormData to multipart/form-data format manually
      const boundary = `--------------------------${Math.random().toString(36).slice(2)}`;
      const chunks: Buffer[] = [];
      let body = '';
      
      // Process each form data entry
      formData.forEach((value, key) => {
        body += `--${boundary}\r\n`;
        body += `Content-Disposition: form-data; name="${key}"`;
        
        // Handle file uploads specially
        if (value instanceof File) {
          body += `; filename="${value.name}"\r\n`;
          body += `Content-Type: ${value.type || 'application/octet-stream'}\r\n\r\n`;
          
          // For files, we need to add the binary data after headers
          chunks.push(Buffer.from(body));
          body = ''; // Reset body string for next part
          
          // We need to read the file as ArrayBuffer and convert to Buffer
          const filePromise = value.arrayBuffer().then(arrayBuffer => {
            chunks.push(Buffer.from(arrayBuffer));
            chunks.push(Buffer.from('\r\n'));
          });
          
          return filePromise;
        } else {
          // For text fields
          body += `\r\n\r\n${value}\r\n`;
        }
      });
      
      // Process all file promises then send the request
      Promise.all(Array.from(formData.entries())
        .filter(([_, value]) => value instanceof File)
        .map(([_, value]) => (value as File).arrayBuffer())
      ).then(fileBuffers => {
        // Add final boundary
        body += `--${boundary}--\r\n`;
        chunks.push(Buffer.from(body));
        
        const postData = Buffer.concat(chunks);
        
        // Create HTTPS request with Node.js https module
        const options = {
          hostname: '16.16.65.102',
          port: 5000,
          path: '/recognize',
          method: 'POST',
          headers: {
            'Content-Type': `multipart/form-data; boundary=${boundary}`,
            'Content-Length': postData.length
          },
          rejectUnauthorized: false // Skip certificate validation
        };
        
        const req = https.request(options, (res) => {
          const chunks: Buffer[] = [];
          res.on('data', (chunk) => chunks.push(chunk));
          res.on('end', () => {
            const body = Buffer.concat(chunks).toString();
            try {
              const data = JSON.parse(body);
              resolve({ status: res.statusCode, data });
            } catch (e) {
              resolve({ 
                status: res.statusCode, 
                data: { error: 'Invalid JSON response', details: body } 
              });
            }
          });
        });
        
        req.on('error', (error) => {
          console.error('Error in HTTPS request:', error);
          reject(error);
        });
        
        req.write(postData);
        req.end();
      }).catch(reject);
    });
    
    console.log('Recognition service response:', response);
    
    if (response.status !== 200) {
      return NextResponse.json({ 
        error: 'Recognition service returned an error',
        details: response.data
      }, { status: response.status || 500 });
    }
    
    // Return the data to the client
    return NextResponse.json(response.data);
  } catch (error) {
    console.error('Error forwarding request to recognition service:', error);
    return NextResponse.json({ 
      error: 'Failed to communicate with recognition service',
      details: error instanceof Error ? error.message : String(error)
    }, { status: 500 });
  }
}
