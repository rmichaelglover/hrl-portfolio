#include "proof.hpp"
#include <filesystem>
#include <iostream>
int main(int argc,char** argv){try{
 if(argc!=2)throw std::runtime_error("Usage: magnum_verify CERTIFICATE_OR_DIRECTORY");
 std::uint64_t checked=0;
 auto verify=[](const std::filesystem::path& p){return magnum::check_certificate(p.string());};
 if(std::filesystem::is_directory(argv[1])){for(const auto& e:std::filesystem::recursive_directory_iterator(argv[1]))if(e.is_regular_file()&&e.path().extension()==".cert"){verify(e.path());++checked;}}
 else{verify(argv[1]);checked=1;}
 if(!checked)throw std::runtime_error("No certificates found");
 std::cout<<"{\"verified_certificates\":"<<checked<<",\"ordering_used\":false}\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
