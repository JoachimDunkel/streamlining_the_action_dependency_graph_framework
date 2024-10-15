#include <gtest/gtest.h>
#include <string>
#include "../src/dependency_creator.cpp"
#include <stdexcept>
#include <gmock/gmock.h>



TEST(DependencyCreatorTest, HelloTest)
{
    EXPECT_EQ(hello_from_cpp(), "hello from cpp");
}

TEST(DependencyCreatorTest, create_type2_depends_exhaustive_has_dep)
{
    auto action1 = Action(std::make_tuple(0, 0), std::make_tuple(1, 1), 1, 0, 0);
    auto action2 = Action(std::make_tuple(1, 1), std::make_tuple(2, 2), 0, 1, 1);
    auto deps = create_type2_dependencies({action1, action2}, DepCreationMethod::EXHAUSTIVE);
    EXPECT_EQ(deps[0], std::make_tuple(1, 0));
}

TEST(DependencyCreatorTest, create_type2_depends_exhaustive_not_has_dep)
{
    auto action1 = Action(std::make_tuple(0, 0), std::make_tuple(1, 1), 0, 0, 0);
    auto action2 = Action(std::make_tuple(1, 1), std::make_tuple(2, 2), 1, 1, 1);
    auto deps = create_type2_dependencies({action1, action2}, DepCreationMethod::EXHAUSTIVE);
    EXPECT_EQ(0, deps.size());
}

TEST(DependencyCreatorTest, create_type2_dependencies_cp)
{
    auto action1 = Action(std::make_tuple(0, 0), std::make_tuple(1, 1), 0, 0, 0);
    auto action2 = Action(std::make_tuple(1, 1), std::make_tuple(2, 2), 1, 1, 1);
    auto deps = create_type2_dependencies({action1, action2}, DepCreationMethod::CP);
    EXPECT_EQ(0, deps.size());
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
