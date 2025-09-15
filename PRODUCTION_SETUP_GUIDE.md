# 🎯 **VAPI-EXOTEL PRODUCTION INTEGRATION GUIDE**

## 📋 **COMPLETE SETUP SCENARIOS & STEPS**

### 🔧 **Prerequisites**

#### **Exotel Account Requirements:**
- Active Exotel account with vSIP API access
- API credentials from: https://my.exotel.com/apisettings/site#api-credentials
- Virtual numbers from: https://my.exotel.com/numbers

#### **Vapi Account Requirements:**
- Active Vapi account: https://dashboard.vapi.ai
- Private API key
- Created AI assistant(s)

#### **Required Environment Variables:**
```bash
# Exotel Configuration
export EXO_AUTH_KEY="your_exotel_api_key_40_chars"
export EXO_AUTH_TOKEN="your_exotel_auth_token_40_chars"
export EXO_ACCOUNT_SID="your_account_sid"
export EXO_SUBSCRIBIX_DOMAIN="api.in.exotel.com"  # or your region

# Vapi Configuration
export VAPI_PRIVATE_KEY="your_vapi_private_key_uuid"
export VAPI_ASSISTANT_ID="your_assistant_id_uuid"

# Integration Settings
export PHONE_NUMBER="+91XXXXXXXXXX"
export VAPI_FQDN="your-bot@sip.vapi.ai"
export EXOTEL_GATEWAY_IP="pstn.mum1.exotel.com"  # or your region gateway
export EXOTEL_GATEWAY_PORT="5070"
```

---

## **SCENARIO 1: FQDN + BYO TRUNK INTEGRATION (Primary Bot)**

### 🎯 **Configuration Template:**
- **FQDN:** `your-bot-1@sip.vapi.ai`
- **Phone Number:** `+91XXXXXXXXXX`
- **Assistant:** `assistant-id-uuid-1`
- **Trunk Name:** `YourBot1Trunk`

### 📝 **Step-by-Step Setup:**

#### **Phase 1: Exotel Trunk Setup**

1. **Create Trunk:**
   ```bash
   curl -X POST "https://api.in.exotel.com/v2/accounts/{ACCOUNT_SID}/trunks" \
     -H "Content-Type: application/json" \
     -H "Authorization: Basic $(echo -n '{AUTH_KEY}:{AUTH_TOKEN}' | base64)" \
     -d '{
       "trunk_name": "YourBot1Trunk",
       "nso_code": "ANY-ANY",
       "domain_name": "{ACCOUNT_SID}.pstn.exotel.com"
     }' \
     --insecure
   ```
   **Result:** `trunk_sid: "trmum_xxxxxxxxxxxxx"`

2. **Add FQDN Destination:**
   ```bash
   curl -X POST "https://api.in.exotel.com/v2/accounts/{ACCOUNT_SID}/trunks/{TRUNK_SID}/destination-uris" \
     -H "Content-Type: application/json" \
     -H "Authorization: Basic $(echo -n '{AUTH_KEY}:{AUTH_TOKEN}' | base64)" \
     -d '{
       "destinations": [{
         "destination": "your-bot-1.sip.vapi.ai:5060;transport=tcp"
       }]
     }' \
     --insecure
   ```
   **Result:** `destination_id: "xxxx"`

3. **Map Phone Number:**
   ```bash
   curl -X POST "https://api.in.exotel.com/v2/accounts/{ACCOUNT_SID}/trunks/{TRUNK_SID}/phone-numbers" \
     -H "Content-Type: application/json" \
     -H "Authorization: Basic $(echo -n '{AUTH_KEY}:{AUTH_TOKEN}' | base64)" \
     -d '{
       "phone_number": "+91XXXXXXXXXX"
     }' \
     --insecure
   ```
   **Result:** `mapping_id: "xxxxx"`

4. **Whitelist Vapi IPs:**
   ```bash
   # IP 1
   curl -X POST "https://api.in.exotel.com/v2/accounts/{ACCOUNT_SID}/trunks/{TRUNK_SID}/whitelisted-ips" \
     -H "Content-Type: application/json" \
     -H "Authorization: Basic $(echo -n '{AUTH_KEY}:{AUTH_TOKEN}' | base64)" \
     -d '{
       "ip": "44.229.228.186",
       "mask": 32
     }' \
     --insecure

   # IP 2
   curl -X POST "https://api.in.exotel.com/v2/accounts/{ACCOUNT_SID}/trunks/{TRUNK_SID}/whitelisted-ips" \
     -H "Content-Type: application/json" \
     -H "Authorization: Basic $(echo -n '{AUTH_KEY}:{AUTH_TOKEN}' | base64)" \
     -d '{
       "ip": "44.238.177.138",
       "mask": 32
     }' \
     --insecure
   ```

#### **Phase 2: Resolve Gateway IP**
```bash
# Get the actual IP of your Exotel gateway
nslookup pstn.mum1.exotel.com
# Result: 129.154.231.198 (example - use your actual result)
```

#### **Phase 3: Vapi BYO Trunk Setup**

5. **Create BYO Credential:**
   ```bash
   curl -X POST "https://api.vapi.ai/credential" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer {VAPI_PRIVATE_KEY}" \
     -d '{
       "provider": "byo-sip-trunk",
       "name": "Your Gateway Name",
       "gateways": [{
         "ip": "129.154.231.198",
         "port": 5070,
         "inboundEnabled": true,
         "outboundEnabled": true
       }],
       "outboundLeadingPlusEnabled": true
     }'
   ```
   **Result:** `credential_id: "uuid-xxxx-xxxx"`

6. **Create Phone Number Resource:**
   ```bash
   curl -X POST "https://api.vapi.ai/phone-number" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer {VAPI_PRIVATE_KEY}" \
     -d '{
       "provider": "byo-phone-number",
       "name": "Your Bot Number",
       "number": "+91XXXXXXXXXX",
       "numberE164CheckEnabled": false,
       "credentialId": "{CREDENTIAL_ID}",
       "assistantId": "{ASSISTANT_ID}"
     }'
   ```
   **Result:** `phone_number_id: "uuid-xxxx-xxxx"`

### 📞 **Call Flow:**
```
Caller dials +91XXXXXXXXXX
    ↓
Exotel receives call
    ↓
Routes to: your-bot-1.sip.vapi.ai:5060;transport=tcp
    ↓
Vapi receives on FQDN: your-bot-1@sip.vapi.ai
    ↓
Your Assistant answers
    ↓
Conversation handled by Vapi AI
```

---

## **SCENARIO 2: MULTIPLE ASSISTANTS SETUP**

### 🎯 **Configuration Template:**
- **FQDN:** `your-bot-2@sip.vapi.ai`
- **Phone Number:** `+91YYYYYYYYYY`
- **Assistant:** `assistant-id-uuid-2`
- **Trunk Name:** `YourBot2Trunk`

### 📝 **Setup Steps:**
Follow the same steps as Scenario 1, but with different values:
- Different trunk name: `YourBot2Trunk`
- Different FQDN: `your-bot-2.sip.vapi.ai`
- Different phone number: `+91YYYYYYYYYY`
- Different assistant ID: `assistant-id-uuid-2`
- **Reuse existing BYO credential** from Scenario 1

---

## **🔧 TECHNICAL ARCHITECTURE**

### **Network Flow:**
```
PSTN Network
    ↓
Exotel Gateway (your-region.exotel.com:5070)
    ↓
Exotel Trunk (IP-WHITELIST auth)
    ↓
SIP Destination (your-fqdn.sip.vapi.ai:5060;transport=tcp)
    ↓
Vapi SIP Infrastructure (44.229.228.186, 44.238.177.138)
    ↓
Vapi AI Assistant
```

### **Key Components:**
1. **Exotel Trunk:** Routes calls from PSTN to Vapi
2. **FQDN Conversion:** `@` → `.` (your-bot@sip.vapi.ai → your-bot.sip.vapi.ai)
3. **IP Whitelisting:** Vapi IPs allowed on Exotel trunk
4. **BYO Credential:** Vapi's connection back to Exotel gateway
5. **Phone Number Resource:** Links DID to specific assistant

---

## **🧪 TESTING SCENARIOS**

### **Test 1: Inbound Call (FQDN Integration)**
```bash
Action: Call your primary number
Expected: Primary assistant answers within 2-3 seconds
Validation: Check call logs for NORMAL_CLEARING
```

### **Test 2: Outbound Call (BYO Trunk)**
```bash
curl -X POST "https://api.vapi.ai/call/phone" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {VAPI_PRIVATE_KEY}" \
  -d '{
    "assistantId": "{ASSISTANT_ID}",
    "customer": {
      "number": "+91XXXXXXXXXX",
      "numberE164CheckEnabled": false
    },
    "phoneNumberId": "{PHONE_NUMBER_ID}"
  }'
```

### **Test 3: Call Status Check**
```bash
curl -X GET "https://api.vapi.ai/call/{CALL_ID}" \
  -H "Authorization: Bearer {VAPI_PRIVATE_KEY}"
```

---

## **📊 MONITORING & TROUBLESHOOTING**

### **Success Indicators:**
- ✅ Call connects within 3 seconds
- ✅ Assistant responds appropriately
- ✅ Call duration > 30 seconds
- ✅ Call ends with NORMAL_CLEARING
- ✅ Audio quality is clear

### **Common Issues & Solutions:**

1. **"Multiple accounts attempting to default route"**
   - **Cause:** Duplicate FQDN/phone number on multiple trunks
   - **Solution:** Remove duplicates from conflicting trunks

2. **"SIP gateway validation failed"**
   - **Cause:** Using domain name instead of IP
   - **Solution:** Use resolved IP address for BYO credential

3. **Call not connecting**
   - **Check:** Vapi IPs whitelisted on trunk
   - **Check:** Phone number mapped to correct trunk
   - **Check:** FQDN destination added correctly

---

## **🎯 PRODUCTION CHECKLIST**

### **Before Go-Live:**
- [ ] All Vapi IPs whitelisted (44.229.228.186, 44.238.177.138)
- [ ] Phone numbers mapped to correct trunks
- [ ] FQDN destinations configured with TCP transport
- [ ] BYO credentials created with correct gateway IP
- [ ] Phone number resources linked to correct assistants
- [ ] Test calls completed successfully
- [ ] Call recording enabled (if required)
- [ ] Monitoring and alerting configured

### **Post Go-Live:**
- [ ] Monitor call success rates
- [ ] Check call duration metrics
- [ ] Verify assistant performance
- [ ] Monitor for routing conflicts
- [ ] Regular testing of both inbound/outbound flows

---

## **🚀 SCALING CONSIDERATIONS**

### **Adding New Assistants:**
1. Create new trunk (if needed)
2. Add FQDN destination
3. Map phone number
4. Create Vapi phone number resource
5. Link to assistant

### **Multiple Phone Numbers per Assistant:**
- Reuse existing BYO credential
- Create additional phone number resources
- Map each DID to appropriate trunk

### **Load Balancing:**
- Multiple FQDN destinations per trunk
- Weight-based routing
- Failover configurations

---

## **📋 COMPLETE API REFERENCE**

### **Exotel APIs Used:**
1. `POST /v2/accounts/{account_sid}/trunks` - Create trunk
2. `GET /v2/accounts/{account_sid}/trunks` - List trunks
3. `POST /trunks/{trunk_sid}/destination-uris` - Add FQDN destination
4. `GET /trunks/{trunk_sid}/destination-uris` - List destinations
5. `POST /trunks/{trunk_sid}/phone-numbers` - Map phone number
6. `GET /trunks/{trunk_sid}/phone-numbers` - List mapped numbers
7. `POST /trunks/{trunk_sid}/whitelisted-ips` - Whitelist IP
8. `GET /trunks/{trunk_sid}/whitelisted-ips` - List whitelisted IPs
9. `GET /trunks/{trunk_sid}/credentials` - List trunk credentials
10. `DELETE /trunks/{trunk_sid}/destination-uris/{id}` - Remove destination
11. `DELETE /trunks/{trunk_sid}/phone-numbers/{id}` - Remove phone mapping
12. `DELETE /trunks?trunk_sid={trunk_sid}` - Delete entire trunk

### **Vapi APIs Used:**
1. `POST /credential` - Create BYO credential
2. `GET /credential` - List credentials
3. `POST /phone-number` - Create phone number resource
4. `GET /phone-number` - List phone numbers
5. `POST /call/phone` - Initiate outbound call
6. `GET /call/{call_id}` - Get call status

### **Additional Utility Commands:**
1. `nslookup {domain}` - Resolve gateway IP
2. `python3 production_integration_script.py --validate-config` - Validate setup
3. `python3 production_integration_script.py --setup-all` - Complete setup
4. `python3 cleanup_resources.py --list-resources` - List all resources
5. `python3 cleanup_resources.py --delete-trunk {trunk_sid}` - Delete trunk

---

## **📋 CURL COMMAND EXAMPLES**

### **Exotel API Examples:**

#### **List All Trunks:**
```bash
curl -X GET "https://api.in.exotel.com/v2/accounts/{ACCOUNT_SID}/trunks" \
  -H "Authorization: Basic $(echo -n '{AUTH_KEY}:{AUTH_TOKEN}' | base64)" \
  --insecure
```

#### **Get Trunk Destinations:**
```bash
curl -X GET "https://api.in.exotel.com/v2/accounts/{ACCOUNT_SID}/trunks/{TRUNK_SID}/destination-uris" \
  -H "Authorization: Basic $(echo -n '{AUTH_KEY}:{AUTH_TOKEN}' | base64)" \
  --insecure
```

#### **Get Trunk Phone Numbers:**
```bash
curl -X GET "https://api.in.exotel.com/v2/accounts/{ACCOUNT_SID}/trunks/{TRUNK_SID}/phone-numbers" \
  -H "Authorization: Basic $(echo -n '{AUTH_KEY}:{AUTH_TOKEN}' | base64)" \
  --insecure
```

#### **Get Whitelisted IPs:**
```bash
curl -X GET "https://api.in.exotel.com/v2/accounts/{ACCOUNT_SID}/trunks/{TRUNK_SID}/whitelisted-ips" \
  -H "Authorization: Basic $(echo -n '{AUTH_KEY}:{AUTH_TOKEN}' | base64)" \
  --insecure
```

#### **Get Trunk Credentials:**
```bash
curl -X GET "https://api.in.exotel.com/v2/accounts/{ACCOUNT_SID}/trunks/{TRUNK_SID}/credentials" \
  -H "Authorization: Basic $(echo -n '{AUTH_KEY}:{AUTH_TOKEN}' | base64)" \
  --insecure
```

#### **Delete Trunk Destination:**
```bash
curl -X DELETE "https://api.in.exotel.com/v2/accounts/{ACCOUNT_SID}/trunks/{TRUNK_SID}/destination-uris/{DEST_ID}" \
  -H "Authorization: Basic $(echo -n '{AUTH_KEY}:{AUTH_TOKEN}' | base64)" \
  --insecure
```

#### **Delete Phone Number Mapping:**
```bash
curl -X DELETE "https://api.in.exotel.com/v2/accounts/{ACCOUNT_SID}/trunks/{TRUNK_SID}/phone-numbers/{MAPPING_ID}" \
  -H "Authorization: Basic $(echo -n '{AUTH_KEY}:{AUTH_TOKEN}' | base64)" \
  --insecure
```

#### **Delete Entire Trunk:**
```bash
curl -X DELETE "https://api.in.exotel.com/v2/accounts/{ACCOUNT_SID}/trunks?trunk_sid={TRUNK_SID}" \
  -H "Authorization: Basic $(echo -n '{AUTH_KEY}:{AUTH_TOKEN}' | base64)" \
  --insecure
```

### **Vapi API Examples:**

#### **List Credentials:**
```bash
curl -X GET "https://api.vapi.ai/credential" \
  -H "Authorization: Bearer {VAPI_PRIVATE_KEY}"
```

#### **List Phone Numbers:**
```bash
curl -X GET "https://api.vapi.ai/phone-number" \
  -H "Authorization: Bearer {VAPI_PRIVATE_KEY}"
```

#### **Delete BYO Credential:**
```bash
curl -X DELETE "https://api.vapi.ai/credential/{CREDENTIAL_ID}" \
  -H "Authorization: Bearer {VAPI_PRIVATE_KEY}"
```

#### **Delete Phone Number Resource:**
```bash
curl -X DELETE "https://api.vapi.ai/phone-number/{PHONE_NUMBER_ID}" \
  -H "Authorization: Bearer {VAPI_PRIVATE_KEY}"
```

---

## **🔐 SECURITY BEST PRACTICES**

1. **Environment Variables:** Never commit credentials to code
2. **API Keys:** Rotate regularly and use least privilege
3. **IP Whitelisting:** Only whitelist required Vapi IPs
4. **SSL/TLS:** Always use secure connections
5. **Monitoring:** Log all API calls and monitor for anomalies

---

## **📞 SUPPORT & RESOURCES**

- **Exotel Documentation:** https://developer.exotel.com/
- **Vapi Documentation:** https://docs.vapi.ai/
- **SIP Trunk Guide:** https://docs.vapi.ai/advanced/sip/sip-trunk
- **Exotel Support:** https://support.exotel.com/
- **Vapi Support:** https://dashboard.vapi.ai/

**🎉 Your production-ready Vapi-Exotel integration is complete!** 