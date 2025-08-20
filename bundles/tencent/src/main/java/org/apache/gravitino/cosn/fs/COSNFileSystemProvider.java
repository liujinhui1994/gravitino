package org.apache.gravitino.cosn.fs;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import org.apache.gravitino.catalog.hadoop.fs.FileSystemProvider;
import org.apache.gravitino.catalog.hadoop.fs.FileSystemUtils;
import org.apache.gravitino.catalog.hadoop.fs.SupportsCredentialVending;
import org.apache.gravitino.credential.Credential;
import org.apache.gravitino.storage.COSNProperties;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.fs.cosn.CosNFileSystem;

import javax.annotation.Nonnull;
import java.io.IOException;
import java.util.Map;

public class COSNFileSystemProvider implements FileSystemProvider, SupportsCredentialVending {


    private static final String COSN_FILESYSTEM_IMPL = "fs.cosn.impl";
    private static final String COSN_SIMPLE_CREDENTIAL =
            "org.apache.hadoop.fs.CosNFileSystem";

    @VisibleForTesting
    public static final Map<String, String> GRAVITINO_KEY_TO_COSN_HADOOP_KEY =
            ImmutableMap.of(
                    COSNProperties.GRAVITINO_COSN_ENDPOINT, "fs.cosn.bucket.region",
                    COSNProperties.GRAVITINO_COSN_ACCESS_KEY_ID, "fs.cosn.userinfo.secretId",
                    COSNProperties.GRAVITINO_COSN_ACCESS_KEY_SECRET, "fs.cosn.userinfo.secretKey");


    @Override
    public FileSystem getFileSystem(@Nonnull Path path, @Nonnull Map<String, String> config) throws IOException {
        Map<String, String> hadoopConfMap =
                FileSystemUtils.toHadoopConfigMap(config, GRAVITINO_KEY_TO_COSN_HADOOP_KEY);
        if (!hadoopConfMap.containsKey(COSN_FILESYSTEM_IMPL)) {
            hadoopConfMap.put(COSN_FILESYSTEM_IMPL, COSN_SIMPLE_CREDENTIAL);
        }

        Configuration configuration = FileSystemUtils.createConfiguration(hadoopConfMap);

        return CosNFileSystem.newInstance(path.toUri(), configuration);
    }

    @Override
    public String scheme() {
        return null;
    }

    @Override
    public String name() {
        return null;
    }

    @Override
    public Map<String, String> getFileSystemCredentialConf(Credential[] credentials) {



        return SupportsCredentialVending.super.getFileSystemCredentialConf(credentials);
    }
}
