// @require_once "std/memory.c3"
// @require_once "std/json.c3"
// @require_once "std/string.c3"
// @require_once "std/fcntl.c3"
// @require_once "std/io.c3"
// @require_once "std/format.c3"

// function main : (argc: int, argv: u8[&][&]) -> int = {
//     let file_to_parse : CString = {&argv[1]};
//     let file : UnbufferedFile = open(file_to_parse, O_RDONLY());

//     let allocator : Allocator = initialize_allocator();
//     let file_contents : Vector<u8> = make_vector<u8>(&allocator);

//     // 1) Read the entire file
//     {
//         let read_buffer : u8[1024];

//         // TODO: `do while` to avoid temp value? Or `break` to make this prettier
//         let read_data : StringView = sv("uninitialized");
//         while read_data.length != 0 {
//             read_data = file:read(sv(&read_buffer));
//             file_contents:extend_back(read_data);
//         }
//     }
//     let program_text : StringView = file_contents:data();

//     let node_opt : Optional<JSON_Node> = json_parse(program_text);

//     if node_opt:has_value() {
//         return 0;
//     }
//     else {
//         return 1;
//     }
// }

@require_once "std/format.c3"

function main : () -> int = {
    print(1, 2, sv("hello!"));
    return 0;
}
