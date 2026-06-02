在[密码学](https://en.wikipedia.org/wiki/Cryptography "密码学")中，**Merkle-Damgård 构造**或**Merkle-Damgård 哈希函数是一种利用抗碰撞**[单向压缩函数构建](https://en.wikipedia.org/wiki/One-way_compression_function "One-way compression function")[抗](https://en.wikipedia.org/wiki/Collision_resistance "碰撞阻力") 碰撞[加密哈希函数](https://en.wikipedia.org/wiki/Cryptographic_hash_function "加密哈希函数")的方法。：145 这种构造被用于设计许多流行的哈希算法，例如[MD5](https://en.wikipedia.org/wiki/MD5 "MD5")、[SHA-1](https://en.wikipedia.org/wiki/SHA-1 "SHA-1")和[SHA-2](https://en.wikipedia.org/wiki/SHA-2 "SHA-2")。
[Merkle-Damgård 构造由Ralph Merkle](https://en.wikipedia.org/wiki/Ralph_Merkle "拉尔夫·默克尔")于1979 年在其[博士](https://en.wikipedia.org/wiki/Doctor_of_Philosophy "哲学博士") [论文](https://en.wikipedia.org/wiki/Thesis "论文")中提出。Ralph Merkle 和[Ivan Damgård](https://en.wikipedia.org/wiki/Ivan_Damg%C3%A5rd "伊万·达姆加德")分别独立证明了该结构的可靠性：也就是说，如果使用合适的[填充方案并且压缩函数是](https://en.wikipedia.org/wiki/Padding_\(cryptography\) "填充（密码学）")[抗碰撞的](https://en.wikipedia.org/wiki/Collision_resistance "碰撞阻力")，那么哈希函数也将是抗碰撞的。[

Merkle-Damgård 哈希函数首先应用[符合 MD 规范的填充](https://en.wikipedia.org/wiki/Merkle%E2%80%93Damg%C3%A5rd_construction#MD-compliant_padding)函数，生成一个长度为固定数字倍数（例如 512 或 1024）的输入——这是因为压缩函数无法处理任意长度的输入。然后，哈希函数将结果分割成固定长度的数据块，并逐个使用压缩函数进行处理，每次处理都将输入块与上一轮的输出合并。为了确保构造的安全性，Merkle 和 Damgård 提出使用长度编码的填充来填充消息。这被称为_长度填充_或_Merkle-Damgård 强化_。

[![](https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Merkle-Damgard_hash_big.svg/500px-Merkle-Damgard_hash_big.svg.png)](https://en.wikipedia.org/wiki/File:Merkle-Damgard_hash_big.svg)

Merkle–Damgård 哈希构造

在图中，单向压缩函数用_f_表示，它将两个固定长度的输入转换为与其中一个输入长度相同的输出。该算法从一个初始值（[初始化向量](https://en.wikipedia.org/wiki/Initialization_vector "初始化向量")(IV)）开始。IV 是一个固定值（算法或实现特定）。对于每个消息块，压缩（或精简）函数_f_会获取当前的结果，将其与该消息块合并，并生成一个中间结果。最后一个消息块会根据需要用零填充，并附加表示整个消息长度的位。（有关详细的长度填充示例，请参见下文。）

为了进一步增强哈希的安全性，有时会将最终结果输入到_终结函数_中。终结函数可以有多种用途，例如将较大的内部状态（最终结果）压缩成较小的输出哈希值，或者确保哈希和中的比特更好地混合和[雪崩效应](https://en.wikipedia.org/wiki/Avalanche_effect "雪崩效应")。终结函数通常使用压缩函数构建。（请注意，在某些文档中使用了不同的术语：长度填充操作被称为“终结”。