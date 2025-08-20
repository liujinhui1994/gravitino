/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *  http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package org.apache.gravitino.storage;

// Properties for cosn.
public class COSNProperties {

  // The region of tencent cosn.
  public static final String GRAVITINO_COSN_REGION = "cosn-region";
  // The endpoint of tencent cosn.
  public static final String GRAVITINO_COSN_ENDPOINT = "cosn-endpoint";
  // The static access key ID used to access cosn data.
  public static final String GRAVITINO_COSN_ACCESS_KEY_ID = "cosn-access-key-id";
  // The static access key secret used to access cosn data.
  public static final String GRAVITINO_COSN_ACCESS_KEY_SECRET = "cosn-secret-access-key";

  // OSS role arn
  public static final String GRAVITINO_COSN_ROLE_ARN = "cosn-role-arn";
  // OSS external id
  public static final String GRAVITINO_COSN_EXTERNAL_ID = "cosn-external-id";

  private COSNProperties() {}
}
