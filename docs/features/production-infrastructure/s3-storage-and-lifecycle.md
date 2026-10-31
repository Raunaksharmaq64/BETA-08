# S3 Storage & Lifecycle Management Guide

## 1. Bucket Topology & Encryption
RIGHT FIT provisions three dedicated, private Amazon S3 buckets:
1. `rightfit-resumes-production`: Candidate resume uploads (PDF, DOCX).
2. `rightfit-reports-production`: Generated interview preparation packages and market exports.
3. `rightfit-backups-production`: PostgreSQL binary dumps and checksum archives.

### Security Enforcements:
- **Block Public Access**: All 4 AWS public access block settings (`BlockPublicAcls`, `BlockPublicPolicy`, `IgnorePublicAcls`, `RestrictPublicBuckets`) set to `true`.
- **Encryption at Rest**: AES-256 Server-Side Encryption (`SSE-S3` or `SSE-KMS`).
- **TLS 1.2+ Enforced**: Bucket policy explicitly denies any request where `aws:SecureTransport == false`.

## 2. Presigned URL Operations
Direct file uploads and downloads bypass public bucket access using temporary presigned URLs managed by `app.core.s3_client.S3StorageClient`:
- **Presigned Upload URL**: Max file size 15MB, strict MIME-type condition (`application/pdf`, `docx`), valid for **15 minutes**.
- **Presigned Download URL**: Restricted to authenticated user who owns the resume record, valid for **15 minutes**.

## 3. Lifecycle Transition Rules
- **Resumes**: Transition to `STANDARD_IA` after 60 days; non-current versions transition to `GLACIER` after 30 days.
- **Backups**: Transition to `STANDARD_IA` after 30 days; `GLACIER` after 90 days; expire after 365 days.
- **Incomplete Uploads**: Abort multipart uploads older than 7 days.

